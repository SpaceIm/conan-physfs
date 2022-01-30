from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class PhysFSConan(ConanFile):
    name = "physfs"
    description = (
        "PhysicsFS is a library to provide abstract access to various "
        "archives. It is intended for use in video games."
    )
    license = "Zlib"
    topics = ("physfs", "physicsfs", "file", "filesystem", "io")
    homepage = "https://icculus.org/physfs"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "zip": [True, False],
        "sevenzip": [True, False],
        "grp": [True, False],
        "wad": [True, False],
        "hog": [True, False],
        "mvl": [True, False],
        "qpak": [True, False],
        "slb": [True, False],
        "iso9660": [True, False],
        "vdf": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "zip": True,
        "sevenzip": True,
        "grp": True,
        "wad": True,
        "hog": True,
        "mvl": True,
        "qpak": True,
        "slb": True,
        "iso9660": True,
        "vdf": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PHYSFS_ARCHIVE_ZIP"] = self.options.zip
        self._cmake.definitions["PHYSFS_ARCHIVE_7Z"] = self.options.sevenzip
        self._cmake.definitions["PHYSFS_ARCHIVE_GRP"] = self.options.grp
        self._cmake.definitions["PHYSFS_ARCHIVE_WAD"] = self.options.wad
        self._cmake.definitions["PHYSFS_ARCHIVE_HOG"] = self.options.hog
        self._cmake.definitions["PHYSFS_ARCHIVE_MVL"] = self.options.mvl
        self._cmake.definitions["PHYSFS_ARCHIVE_QPAK"] = self.options.qpak
        self._cmake.definitions["PHYSFS_ARCHIVE_SLB"] = self.options.slb
        self._cmake.definitions["PHYSFS_ARCHIVE_ISO9660"] = self.options.iso9660
        self._cmake.definitions["PHYSFS_ARCHIVE_VDF"] = self.options.vdf
        self._cmake.definitions["PHYSFS_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["PHYSFS_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["PHYSFS_BUILD_TEST"] = False
        self._cmake.definitions["PHYSFS_BUILD_DOCS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        target = "physfs" if self.options.shared else "physfs-static"
        self.cpp_info.set_property("cmake_file_name", "PhysFS")
        self.cpp_info.set_property("cmake_target_name", target)
        self.cpp_info.set_property("pkg_config_name", "physfs")
        suffix = "-static" if self._is_msvc and not self.options.shared else ""
        self.cpp_info.libs = ["physfs{}".format(suffix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
