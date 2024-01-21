from distutils.core import setup
import py2exe

setup(
        options = {"py2exe" : {"compressed": 1}},
        windows = [{"script":"classicexe.py"}],
    data_files = [('img', [r"C:/Users/antoi/Documents/Python/ffxivclassic2sim/p2-waymarks.png"]),('img', [r"C:/Users/antoi/Documents/Python/ffxivclassic2sim/Blue.png"]),('img', [r"C:/Users/antoi/Documents/Python/ffxivclassic2sim/Green.png"]),('img', [r"C:/Users/antoi/Documents/Python/ffxivclassic2sim/Orange.png"]),('img', [r"C:/Users/antoi/Documents/Python/ffxivclassic2sim/Purple.png"]),
            ('img', [r"C:/Users/antoi/Documents/Python/ffxivclassic2sim/data.terrain"]),('img', [r"C:/Users/antoi/Documents/Python/ffxivclassic2sim/hardmode.data"])],
        zipfile = None
        )
