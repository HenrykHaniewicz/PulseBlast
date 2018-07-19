# PulseBlast
Basic python package to work with creating pulsar templates and radio frequency interference excision.

**Mac Setup:**

After cloning both PulseBlast and PyPulse (as needed), add PulseBlast and PyPulse to your PYTHONPATH in .bashrc as follows:

```bash
export PYTHONPATH=[directory_for_python3]:[directory_for_pypulse]:[directory_for_pulseblast]:$PYTHONPATH
```

and add an update check in .bash_profile (if not already set up):

```bash
test -f ~/.bashrc && source ~/.bashrc
```

**Usage:**

To do timing, run the following command in the terminal:

```shell
python main.py -f [text files containing directories and / or files] -t [frequency band] --temp [full path to template]
```

To create templates, create a file and initialize the Template class. Each directory being used should be separated by a comma. e.g.:

```python
templateobject = Template( directory1, directory2, directory3 )
```

Once the class is initialized, run

```python
templateobject.createTemplate( filename_to_save, directory_to_save_to )
```

**Requires:**  

Python 3.X  

PyPulse  
Numpy v1.14.5  
Scipy v1.1.0  
Astropy v3.0.3  
Matplotlib v2.2.2
