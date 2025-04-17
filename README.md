# checkers-in-pdf
This is a game of checkers contained within a pdf file. Works in Firefox and chrome (probably other chromium browsers too). The chromium version is a bit buggy with lines sometimes not refreshing properly, but it works.

<img width="310" alt="Screenshot 2025-04-17 at 8 28 10 AM" src="https://github.com/user-attachments/assets/81b6594f-abbe-456d-8ba2-be3bf6a4882a" />

A lot of the concepts here (and the basic structure) are taken from Thomas Rinsma's PDF tetris: https://github.com/ThomasRinsma/pdftris

This only works because Firefox and Chromium's pdf readers support a bit Javascript for me to write the checkers logic. Again, check out Rinsma's explanation to learn more. 

To render the board and pieces Rinsma's PDF tetris taught me to abuse the form filling functionality in PDF.js (Firefox PDF reader) and PDFium (Chromium PDF reader). I can create buttons for the grids and pieces from the PDF's Javascript code, fields to print information, and alerts to have a little pop up when the game ends. 

This was pretty fun, I had no idea pdfs could do cursed things like this.

### Further information:


Mozilla's explanation for adding form filling support - https://hacks.mozilla.org/2021/10/implementing-form-filling-and-accessibility-in-the-firefox-pdf-viewer/



