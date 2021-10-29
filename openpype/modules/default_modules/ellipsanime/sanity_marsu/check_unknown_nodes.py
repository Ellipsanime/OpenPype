import sys
import maya.cmds as cmds


unknown_nodes = []


def name():
    return 'Unknown Nodes'


def check(stream=sys.stdout):
    global unknown_nodes
    unknown_nodes = cmds.ls(type='unknown')

    if unknown_nodes:
        for item in unknown_nodes:
            stream.write(item)
            stream.write('\n')
        return False

    return True


def highlight(stream=sys.stdout):
    if unknown_nodes:
        cmds.select(unknown_nodes)


def resolve(stream=sys.stdout):
    if unknown_nodes:
        try:
            cmds.lockNode(unknown_nodes, lock=False)
            cmds.delete(unknown_nodes)
        except Exception as err:
            stream.write(str(err))
            stream.write('\n')




if __name__ == "__main__":
    ok = check()
    if not ok:
        print unknown_nodes
