import tkinter as tk
import webbrowser
from PIL import Image, ImageTk


class ContributorWallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NexaPod Contributor Wall")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2E2E2E")

        self.title_label = tk.Label(
            root,
            text="Nexapod Contributor Wall",
            font=("Helvetica", 24, "bold"),
            bg="#2E2E2E",
            fg="#FFFFFF",
        )
        self.title_label.pack(pady=20)

        self.canvas = tk.Canvas(root, bg="#2E2E2E", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(
            root, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.contributors_frame = tk.Frame(self.canvas, bg="#2E2E2E")
        self.canvas.create_window(
            (0, 0), window=self.contributors_frame, anchor=tk.NW
        )

        self.contributors_data = [
            {
                "name": "Kunya",
                "image_path": "assets/kunya.png",
                "github_url": "https://github.com/kunya66",
            },
            {
                "name": "ChatGPT",
                "image_path": "assets/chatgpt.png",
                "github_url": "https://github.com/chatgpt",
            },
            {
                "name": "Gemini",
                "image_path": "assets/gemini.png",
                "github_url": "https://github.com/gemini",
            },
            {
                "name": "Claude",
                "image_path": "assets/claude.png",
                "github_url": "https://github.com/claude",
            },
            {
                "name": "Other Contributor 1",
                "image_path": "assets/default.png",
                "github_url": "https://github.com/contributor1",
            },
            {
                "name": "Other Contributor 2",
                "image_path": "assets/default.png",
                "github_url": "https://github.com/contributor2",
            },
            {
                "name": "Other Contributor 3",
                "image_path": "assets/default.png",
                "github_url": "https://github.com/contributor3",
            },
            {
                "name": "Other Contributor 4",
                "image_path": "assets/default.png",
                "github_url": "https://github.com/contributor4",
            },
            {
                "name": "Other Contributor 5",
                "image_path": "assets/default.png",
                "github_url": "https://github.com/contributor5",
            },
            {
                "name": "Other Contributor 6",
                "image_path": "assets/default.png",
                "github_url": "https://github.com/contributor6",
            },
        ]

        self.create_contributor_widgets()
        self.contributors_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_contributor_widgets(self):
        for i, contributor in enumerate(self.contributors_data):
            row, col = divmod(i, 4)
            contributor_frame = tk.Frame(
                self.contributors_frame,
                bg="#3C3C3C",
                relief=tk.RAISED,
                borderwidth=2,
            )
            contributor_frame.grid(
                row=row, column=col, padx=20, pady=20, sticky="nsew"
            )

            try:
                img = Image.open(contributor["image_path"])
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                image_label = tk.Label(
                    contributor_frame, image=photo, bg="#3C3C3C"
                )
                image_label.image = photo
                image_label.pack(pady=10)
            except FileNotFoundError:
                # Handle case where image is not found
                placeholder_label = tk.Label(
                    contributor_frame,
                    text="Image not found",
                    bg="#3C3C3C",
                    fg="#FFFFFF",
                )
                placeholder_label.pack(pady=10)

            name_label = tk.Label(
                contributor_frame,
                text=contributor["name"],
                font=("Helvetica", 12, "bold"),
                bg="#3C3C3C",
                fg="#FFFFFF",
            )
            name_label.pack()

            github_link = tk.Label(
                contributor_frame,
                text="GitHub Profile",
                font=("Helvetica", 10, "underline"),
                fg="#1E90FF",
                bg="#3C3C3C",
                cursor="hand2",
            )
            github_link.pack(pady=5)
            github_link.bind(
                "<Button-1>",
                lambda e, url=contributor["github_url"]: self.open_link(url),
            )

    def open_link(self, url):
        webbrowser.open_new(url)


def main():
    root = tk.Tk()
    ContributorWallApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
