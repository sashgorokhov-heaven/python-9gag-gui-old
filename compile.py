from cx_Freeze import setup, Executable

executables = [
    Executable("gag.py",
               #icon="Resourses\\icon.png",
               appendScriptToExe=True,
               appendScriptToLibrary=True,
    )
]

buildOptions = dict(create_shared_zip=True,
                    include_files=('Resourses', 'Resourses'),
                    silent=True)

setup(name="9GAG Project",
      version="1.0",
      description="The 9GAG Project",
      options={'build_exe': buildOptions},
      executables=executables,
)