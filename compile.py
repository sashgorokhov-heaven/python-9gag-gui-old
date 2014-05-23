from cx_Freeze import setup, Executable

print('\nPyQt4 NEED SOME CHANGES\n')

executables = [
    Executable("gag.py",
               appendScriptToExe=True,
               appendScriptToLibrary=True,
    ),
    Executable("autoposter.py",
               appendScriptToExe=True,
               appendScriptToLibrary=True,
    ),
    Executable("delete_repeats.py",
               appendScriptToExe=True,
               appendScriptToLibrary=True,
    )
]

buildOptions = dict(create_shared_zip=True,
                    include_files=('resourses', 'resourses'),
                    silent=True)

setup(name="9GAG Project",
      version="3.0",
      description="The 9GAG Project",
      options={'build_exe': buildOptions},
      executables=executables,
)