# PulseBlast
Basic python package to work with creating pulsar templates and radio frequency interference excision.

To do timing, run the following command in the terminal:

```bash
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

Requires:  

Python 3.X  

PyPulse  
Numpy v1.14.2  
Scipy v1.0.1  
Astropy v3.0.1  
Matplotlib v2.2.2
