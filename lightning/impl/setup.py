import os.path

import numpy


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration('impl', parent_package, top_path)

    randomdir = os.path.join(top_path, "lightning", "impl", "random")

    config.add_extension('dataset_fast',
                         sources=['dataset_fast.cpp'],
                         include_dirs=[numpy.get_include(), randomdir])

    config.add_extension('dual_cd_fast',
                         sources=['dual_cd_fast.cpp'],
                         include_dirs=[numpy.get_include(), randomdir])

    config.add_extension('loss_fast',
                         sources=['loss_fast.cpp'],
                         include_dirs=[numpy.get_include(), randomdir])

    config.add_extension('prank_fast',
                         sources=['prank_fast.cpp'],
                         include_dirs=[numpy.get_include(), randomdir])

    config.add_extension('primal_cd_fast',
                         sources=['primal_cd_fast.cpp'],
                         include_dirs=[numpy.get_include(), randomdir])

    config.add_extension('sgd_fast',
                         sources=['sgd_fast.cpp'],
                         include_dirs=[numpy.get_include(), randomdir])

    config.add_subpackage('datasets')
    config.add_subpackage('random')
    config.add_subpackage('tests')

    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
