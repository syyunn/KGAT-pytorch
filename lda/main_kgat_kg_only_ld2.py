from utility.parser_kgat import *
from utility.log_helper import *
import random
import numpy as np
import torch
import torch.optim as optim

from time import time

from lda.custom.utility.loader_kgat import DataLoaderKGAT
from lda.custom.model.KGAT import *

def train(args):
    # seed
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    print("args.save_dir: ", args.save_dir)
    log_save_id = create_log_id(args.save_dir)
    logging_config(
        folder=args.save_dir, name="log{:d}".format(log_save_id), no_console=False
    )
    logging.info(args)

    # GPU / CPU
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_gpu = torch.cuda.device_count()
    print("n_gpu: ", n_gpu)
    if n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)

    data = DataLoaderKGAT(args, logging)
    print(data)

    if args.use_pretrain == 1:
        user_pre_embed = torch.tensor(data.user_pre_embed)
        item_pre_embed = torch.tensor(data.item_pre_embed)
    else:
        user_pre_embed, item_pre_embed = None, None

    # construct model & optimizer
    model = KGAT(
        args,
        data.n_entities,
        data.n_relations,
        user_pre_embed,
        item_pre_embed,
    )

    print(model)

    model.to(device)
    # if n_gpu > 1:
    #     model = nn.parallel.DistributedDataParallel(model)
    logging.info(model)

    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    # move graph data to GPU
    train_graph = data.train_graph
    train_nodes = torch.LongTensor(train_graph.ndata["id"])
    train_edges = torch.LongTensor(train_graph.edata["type"])
    if use_cuda:
        train_nodes = train_nodes.to(device)
        train_edges = train_edges.to(device)
    train_graph.ndata["id"] = train_nodes
    train_graph.edata["type"] = train_edges

    test_graph = data.test_graph
    test_nodes = torch.LongTensor(test_graph.ndata["id"])
    test_edges = torch.LongTensor(test_graph.edata["type"])
    if use_cuda:
        test_nodes = test_nodes.to(device)
        test_edges = test_edges.to(device)
    test_graph.ndata["id"] = test_nodes
    test_graph.edata["type"] = test_edges

    # initialize metrics
    best_epoch = -1
    epoch_list = []
    precision_list = []
    recall_list = []
    ndcg_list = []

    # train model
    for epoch in range(1, args.n_epoch + 1):
        time0 = time()
        model.train()

        # update attention scores
        with torch.no_grad():
            att = model("calc_att", train_graph)
        train_graph.edata["att"] = att
        logging.info(
            "Update attention scores: Epoch {:04d} | Total Time {:.1f}s".format(
                epoch, time() - time0
            )
        )

        # train kg
        time1 = time()
        kg_total_loss = 0
        n_kg_batch = data.n_kg_train // data.kg_batch_size + 1

        for iter in range(1, n_kg_batch + 1):
            time2 = time()
            (
                kg_batch_head,
                kg_batch_relation,
                kg_batch_pos_tail,
                kg_batch_neg_tail,
            ) = data.generate_kg_batch(data.train_kg_dict)
            if use_cuda:
                kg_batch_head = kg_batch_head.to(device)
                kg_batch_relation = kg_batch_relation.to(device)
                kg_batch_pos_tail = kg_batch_pos_tail.to(device)
                kg_batch_neg_tail = kg_batch_neg_tail.to(device)
            kg_batch_loss = model(
                "calc_kg_loss",
                kg_batch_head,
                kg_batch_relation,
                kg_batch_pos_tail,
                kg_batch_neg_tail,
            )

            kg_batch_loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            kg_total_loss += kg_batch_loss.item()

            if (iter % args.kg_print_every) == 0:
                logging.info(
                    "KG Training: Epoch {:04d} Iter {:04d} / {:04d} | Time {:.1f}s | Iter Loss {:.4f} | Iter Mean Loss {:.4f}".format(
                        epoch,
                        iter,
                        n_kg_batch,
                        time() - time2,
                        kg_batch_loss.item(),
                        kg_total_loss / iter,
                    )
                )
        logging.info(
            "KG Training: Epoch {:04d} Total Iter {:04d} | Total Time {:.1f}s | Iter Mean Loss {:.4f}".format(
                epoch, n_kg_batch, time() - time1, kg_total_loss / n_kg_batch
            )
        )


if __name__ == "__main__":
    args = parse_kgat_args()
    train(args)
    # predict(args)
