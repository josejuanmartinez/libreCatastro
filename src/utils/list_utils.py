class ListUtils:
    """ Different functions for make working with lists easier"""
    def __init__(self):
        pass

    @staticmethod
    def flat(non_flat_list):
        return [item for sublist in non_flat_list for item in sublist]
