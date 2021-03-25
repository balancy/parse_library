# Library parser

Script allows parsing Sci Fi books from [tululu.org](https://tululu.org/). It parses book title, author, genres, image, comments and text if they are present.

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
&nbsp;&nbsp;&nbsp;
For Windows:
```console
env\scripts\activate
```

4. Install dependencies:
```
pip install -r requirements.txt
```

## How to use

General way to use it is via command:

```console
python main.py --start_page start --end_page end
```
where 
- `start` is the page to start download books from
- `end` is the page to finish download books at. This argument isn't necessary. Without it, the script will only 
  download books from the `start` page. 

Complete list of script arguments :

```console
--books_folder folder
``` 
&nbsp;&nbsp;&nbsp;
where folder is the folder to save text versions of books. By default, folder is 'books/'

```console
--imgs_folder folder
``` 
&nbsp;&nbsp;&nbsp;
where folder is the folder to save cover images of books. By default, folder is 'images/'

```console
--json_path folder
``` 
&nbsp;&nbsp;&nbsp;
where folder is the folder to save all downloaded library info in JSON format. By default, folder is root folder.  

```console
--skip_images
``` 
&nbsp;&nbsp;&nbsp;
If this argument given (flag enabled), then script will skip books cover images downloading.  

```console
--skip_txt
``` 
&nbsp;&nbsp;&nbsp;
If this argument given (flag enabled), then script will skip books text versions downloading.  

You can always see the help how to use script by command:
```console
python main.py -h
```