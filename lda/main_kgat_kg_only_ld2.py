from utility.parser_kgat import *
from utility.log_helper import *
import random
import numpy as np
import torch


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


if __name__ == "__main__":
    args = parse_kgat_args()
    train(args)
    # predict(args)
