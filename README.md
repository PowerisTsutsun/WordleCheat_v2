# Wordle Solver
A Tkinter-based Wordle Solver that helps you solve Wordle puzzles by suggesting words based on feedback (green, yellow, grey).

# 📁 Folder Structure

```
wordle_solver_project/
├── app.py                      # Main Tkinter GUI script
├── words.json                  # JSON file with 5-letter words
├── assets/                     # Optional folder for icons, fonts, etc.
│   ├── logo.ico                # (Optional) Custom window icon
│   └── custom_font.ttf         # (Optional) Custom font
└── README.md                   # Project documentation
```

#🚀 Features

- Suggests a random starting word from words.json.
- Allows the user to input feedback (green, yellow, grey) for each guess.
- Filters possible words based on feedback and suggests the next best guess.
- Shows a victory banner when the word is guessed correctly.
- Reset game and keyboard support (Enter, Backspace).

## 🛠️ Setup Instructions
### 1️⃣ Clone the repository
```
git clone https://github.com/yourusername/wordle_solver_project.git
cd wordle_solver_project
```

### 2️⃣ Install Python dependencies

```
python app.py
```
 ### 4️⃣ Add words.json

 ```
 {
    "words": [
        "apple",
        "grape",
        "snack",
        "trend",
        "pitch",
        ...
    ]
}
```

# 🤝 Contributing
Feel free to fork the repo, improve the solver, and submit pull requests! 💡