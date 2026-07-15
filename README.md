## Prerequisites

Before running this project, make sure the following software is installed on your system:

### 1. Python

Install **Python 3.8 or later**.

Download:
https://www.python.org/downloads/

Verify the installation:

```bash
python --version
```

### 2. pip (Python Package Manager)

`pip` is included with Python.

Verify the installation:

```bash
pip --version
```

### 3. Git

Git is required to clone the repository.

Download:
https://git-scm.com/downloads

Verify the installation:

```bash
git --version
```

### 4. Required Python Packages

Install all required packages using:

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the required packages manually:

```bash
pip install django
pip install pandas
pip install numpy
pip install scikit-learn
pip install matplotlib
pip install seaborn
pip install joblib
```

### 5. Database

This project uses **SQLite3**, which is included with Python. No separate installation is required.

Apply the database migrations using:

```bash
python manage.py migrate
```

### 6. Code Editor (Optional)

A code editor is recommended for viewing or modifying the source code.

Recommended editors:
- Visual Studio Code
- PyCharm
