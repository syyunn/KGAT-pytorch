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

if __name__ == "__main__":
    args = parse_kgat_args()
    train(args)
    # predict(args)
