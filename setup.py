import os
from pathlib import Path
from setuptools import Extension
from setuptools.command.build_ext import build_ext

from setuptools import setup, find_packages


class CMakeExtension(Extension):
    def __init__(self, name):
        super().__init__(name, sources=[])


class BuildExt(build_ext):
    def run(self):
        for ext in self.extensions:
            if isinstance(ext, CMakeExtension):
                self.build_cmake(ext)
        super().run()

    def build_cmake(self, ext):
        cwd = Path().absolute()
        build_temp = cwd / ext.name / "build"
        os.makedirs(build_temp, exist_ok=True)
        extdir = Path(self.get_ext_fullpath(ext.name))
        extdir.mkdir(parents=True, exist_ok=True)

        config = "Debug" if self.debug else "Release"
        cmake_args = [
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + str(extdir.parent.absolute()),
            "-DCMAKE_BUILD_TYPE=" + config
        ]

        build_args = [
            "--config", config,
            "--", "-j8"
        ]

        os.chdir(build_temp)
        self.spawn(["cmake", f"{str(cwd)}/{ext.name}"] + cmake_args)
        if not self.dry_run:
            self.spawn(["cmake", "--build", "."] + build_args)
        os.chdir(str(cwd))


src = CMakeExtension("src")

setup(
    name='pystreamvbyte',
    version='0.4.1',
    packages=find_packages(),
    install_requires=['numpy', 'cffi'],
    setup_requires=['cffi', 'wheel'],
    cffi_modules=['streamvbyte/build.py:ffibuilder'],
    ext_modules=[src],
    cmdclass={"build_ext": BuildExt}
)

