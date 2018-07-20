# PulseBlast
Basic python package to work with creating pulsar templates and radio frequency interference excision.

## **Mac Setup:**

After cloning both PulseBlast and PyPulse (as needed), add PulseBlast and PyPulse to your PYTHONPATH in .bashrc as follows:

```bash
export PYTHONPATH=[directory_for_python3]:[directory_for_pypulse]:[directory_for_pulseblast]:$PYTHONPATH
```

and add an update check in .bash_profile (if not already set up):

```bash
test -f ~/.bashrc && source ~/.bashrc
```

## **Usage:**

**Timing**

To get Times-of-Arrival (TOAs), run the following command in the terminal:

```shell
python main.py -f [text files containing directories and / or files] -t [frequency band] --temp [full path to template] -s [sub-integrations to scrunch to]
```

Text files should just contain directories (ending in a "/") or files (ending in a ".???"). E.g. `input.txt`:

```
/Users/User1/Pulsars/directory1/
/Users/User2/PSRs/directory/
/Users/User1/Pulsars/directory2/file1.fits
/Users/User1/Pulsars/directory2/file2.fits
/Users/User2/otherPSRs/profile.fits
```

Directories / files inside the text file need not be in any particular order.

TOAs will be printed to the screen in TEMPO2 format (likely to be improved in the near future).

**Templates**

To create templates, create a file (or run from a python terminal shell) and initialize the Template class with the frequency band required (as a string) and the directories (also as strings).
Each directory being used should be separated by a comma. e.g.:

```python
from PSRTemplate import Template

templateobject = Template( band, directory1, directory2, ..., directoryN )
```

Once the class is initialized, run

```python
templateobject.createTemplate( filename_to_save, directory_to_save_to )
```

## **Requires:**  

Python 3.X  

PyPulse  
Numpy v1.14.5  
Scipy v1.1.0  
Astropy v3.0.3  
Matplotlib v2.2.2
