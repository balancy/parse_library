# Library parser

Script allows parsing books from [tululu.org](https://tululu.org/). It parses book title, author, genre, image, comments and text if they are present.

### How to install

Python3 and Git should be already installed. 

1. Clone the repository by command:
```console
git clone https://github.com/balancy/parse_library
```

2. Go inside cloned repository and create virtual environment by command:
```console
python -m venv env
```

3. Activate virtual environment. For linux-based OS:
```console
source env/bin/activate
```
For Windows:
```console
env\scripts\activate
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Run the script by command:
```console
python main.py start_id end_id
```
where 
- `start_id` is the book id to start parsing with
- `end_id` is the book id to end parsing with
