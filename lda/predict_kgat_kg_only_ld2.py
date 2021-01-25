from utility.parser_kgat import *
from utility.log_helper import *
import random
import numpy as np
import torch
import torch.optim as optim

from time import time

from lda.custom.utility.loader_kgat import DataLoaderKGAT
from lda.custom.model.KGAT import *
from utility.helper import *


def predict(args):
    # GPU / CPU
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_gpu = torch.cuda.device_count()
    if n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)

    data = DataLoaderKGAT(args, logging)
    print(data)

    # construct model & optimizer
    model = KGAT(
        args,
        data.n_entities,
        data.n_relations,
        None,
        None,
    )

    print(model)

    # load model
    epoch=250
    pretrained_model_path = 'trained_model/KGAT/lda/entitydim64_relationdim64_bi-interaction_64-32-16_lr0.0001_pretrain0/model_epoch{}.pth'.format(epoch)
    model = load_model(model, pretrained_model_path)
    model.to(device)
    # if n_gpu > 1:
    #     model = nn.parallel.DistributedDataParallel(model)
    logging.info(model)

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

    model.eval()

    with torch.no_grad():
        att = model("calc_att", train_graph)
    train_graph.edata["att"] = att
    logging.info(
            "Update attention scores:"
    )

    # predict kg
    n_kg_batch = data.n_kg_train // data.kg_batch_size + 1
    # assert n_kg_batch == 1
    print("n_kg_batch: ", n_kg_batch)

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

    print(
        "KG Predict: loss {}".format(
            kg_batch_loss
        )
    )


if __name__ == "__main__":
    args = parse_kgat_args()
    predict(args)
