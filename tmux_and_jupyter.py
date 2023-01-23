import sys
import libtmux
import os
from tqdm import tqdm
import argparse
import secrets
import logging
from logging.handlers import MemoryHandler
from logging import StreamHandler


final_logger = logging.getLogger()
final_logger.setLevel(logging.INFO)
final_logger.addHandler(MemoryHandler(100, target=StreamHandler()))

server = libtmux.Server()

def start(num_users, ports, base_dir='./', session_name='session'):
    """
    Start $num_users jupyter notebooks, each has its working directory $base_dir+$folder_num
    """
    assert num_users <= len(ports), f'Not enough ports. Assign {num_users - len(ports)} more ports.'
    if num_users < len(ports):
        print(f'Using first {num_users} ports out of {len(ports)} available.')
    
    session = server.new_session(session_name)
    windows = []
    panes = []

    for i in tqdm(range(num_users)):
        win = session.new_window(attach=False, window_name="win"+str(int(i)))
        windows.append(win)
        panes.extend(win.list_panes())

        new_dir_path = base_dir + 'new_dir' + str(i)
        os.mkdir(new_dir_path)
        command_cd = f'cd {new_dir_path}'
        token = secrets.token_urlsafe(16)
        command_jupyter = f"jupyter notebook --ip 0.0.0.0 --port {ports[i]} --no-browser --NotebookApp.token='{token}' --NotebookApp.notebook_dir='{base_dir}'" 

        panes[i].send_keys(command_cd)
        panes[i].send_keys(command_jupyter)

        final_logger.info(f'Jupyter Notebook has been created: id={i}, port={ports[i]}, token={token}')


def stop(num, session_name='session'):
    """
    @:param session_name: name of tmux session, in which environments are set
    @:param num: num of environment that is needed to be killed 
    """
    session = server.find_where({'session_name': session_name})
    session.kill_window(num)
    print(f'Jypyter notebook with id={num} has been killed')


def stop_all(session_name='session'):
    """
    @:param session_name: name of tmux session, in which environments are set
    """
    server.kill_session(session_name)
    print(f"Session '{session_name}' has been killed")


def conf_parser():
    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers(dest='command')
    start_parser = subparser.add_parser('start')
    start_parser.add_argument('N', type=int)

    stop_parser = subparser.add_parser('stop')
    stop_parser.add_argument('id', type=int) 

    stop_all_parser = subparser.add_parser('stop_all')
    stop_all_parser.add_argument('x', action='store_true')
    
    return parser


def main(args):
    if args.command == 'start':
        # list of ports
        try: 
            with open('./ports.txt', 'r') as f:
                my_ports = list(map(int, f.read().split()))
        except FileNotFoundError:
            # my_ports = [10246, 10247, 10248, 10249, 10250]
            print('Please, specify available ports in ports.txt file as follows: port1 port2 ...')
            sys.exit(1)
            
        start(args.N, my_ports)
    elif args.command == 'stop':
        stop(args.id)
    elif args.command == 'stop_all':
        stop_all()


if __name__ == '__main__':
    parser = conf_parser()
    args = parser.parse_args()
    main(args) 





