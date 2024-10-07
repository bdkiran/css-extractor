# CSS Extractor

## Installation

1. Create a Python Virtual Environment
You can use `conda` or something else, this is the fastest for me.
```
python -m venv /path/to/new/virtual/environment
```

2. Download Dependencies
Make sure to activate your virtual environment before running!
```
pip3 install -r requirements.txt
```


## Useage

### HTML CSS Class Extraction

### CSS Class Extraction and Compression

## Why?

I like building websites with raw CSS but building UI's with it can be hard and annoying. I'm also not the most creative and it's a pain to write, so I end up copying elements or sections of content that I see on the internet. 

After doing years of manual extraction of sites styles that I like, I decied to make a library that could do this for me. This library has saved me hours of manually reading through markup files and allows me to experiement much quicker.

## How does it work?

The first interation used regex to find and grab the css defintions from our desired input classes. This method actually turned out to be a bad approach because css is complicated expescially when you're dealing with @media queries and psudo selectors. There are some leftover functions that use regex matching, since I didn't bother to rewrite.

I ended up picking up the `tinycss` library that handles parsing text into into a way that it can be programatically analyzed. This is way better to used with @media handlers and psudo selectors. This approach is a bit slow since we're doing this in a bunch of nested loops and the library is not built for speed. Once we iron out edge cases we can look at how we can improve the speed of the program.

## Caveats

This is a very basic implementation. This has gotten me pretty far. There are cetain edge cases that the library does not catch. There are instances of classes that are nested (A child element within a parent element with a certain class). Not selectors are tricky and not caught. Feel free to add a issue for these bugs you find. If it's feasable we'll fix it.