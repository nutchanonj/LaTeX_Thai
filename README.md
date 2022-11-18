# LaTeX for Thai Language :city_sunset:

Trying to use Thai language parallel with all of the stuffs (code listing, maths environment, etc.) in LaTeX can induce pain. 

This is my [LaTeX for Thai script "starter kits"](https://github.com/nutchanonj/LaTeX_Thai) for those who want to getting start with typing LaTeX documents in Thai, but don't know where to begin.

Note:
1. For those who don't even install LaTeX things in Windows, please refer to [this page](https://mjcb.io/blog/2020/01/23/visual-studio-code-with-latex/). To be honest, I found that working with LaTeX in VS Code is the most comfortable way to do things (auto-completion, beautiful dark-mode, very friendly GUI, etc.) Also, Installing MikTeX with Strawberry Perl is much faster (less than 15 minutes with normal internet) than installing TeX Live (more than 2 hours, for real?)
2. Since Thai-script LaTeX needs XeLeTeX to compile the file, I recommend that you make that be default. In VS Code, use the shortcut `CTRL + SHIFT + P` and search for `Preferences: Open User Setting (JSON)`. Then, add this following parameter:

    ```json
    "latex-workshop.latex.tools": [{
        "name": "latexmk",
        "command": "latexmk",
        "args": [
            "-xelatex",
            "-synctex=1",
            "-interaction=nonstopmode",
            "-file-line-error",
            "%DOC%"
        ]
    }]
    ```

3. If you have problems with the font "TH Sarabun New", try "install for all user" when you install the font in Windows.
4. Normally, VS Code will compile your TeX file every time you save it. (If you have followed all of the steps in [this page](https://mjcb.io/blog/2020/01/23/visual-studio-code-with-latex/).)
5. Please note that, unlike many Thai LaTeX preambles that I found so far, my LaTeX preamble does not contain `polyglossia` package. I find it to be a pain in my a$$. It has a lot of problems when using paralelly with `listing` package.
