# Slightly bitten site

Minimalistic blog website basically for hosting folders with `Jinja` templates.

 - One file - one page
 - Color themes
 - Flexible settings
 - JSless mode
 - Cool dog cube on errors


## Startup

By command:
``` bash
gunicorn wsgi:app
```
Optionally with arguments like `--bind unix:./site.sock` and others.


## License

[MIT License](LICENSE.txt)