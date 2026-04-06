import gradio as gr


def parse_playlist(text):
    """
    Convert user input into a list of song dictionaries.
    Expected format per line:
    title, artist, energy, duration
    """
    songs = []
    lines = text.strip().split("\n")

    for i, line in enumerate(lines, start=1):
        parts = [part.strip() for part in line.split(",")]

        if len(parts) != 4:
            raise ValueError(
                f"Line {i} is invalid. Each line must have exactly 4 values: "
                "title, artist, energy, duration"
            )

        title, artist, energy, duration = parts

        try:
            energy = int(energy)
            duration = float(duration)
        except ValueError:
            raise ValueError(
                f"Line {i} has invalid energy or duration. "
                "Energy must be an integer and duration must be a number."
            )

        if not (0 <= energy <= 100):
            raise ValueError(f"Line {i}: energy must be between 0 and 100.")

        songs.append({
            "title": title,
            "artist": artist,
            "energy": energy,
            "duration": duration
        })

    return songs


def format_playlist(songs):
    """Turn the playlist into readable text."""
    if not songs:
        return "No songs to display."

    output = []
    for i, song in enumerate(songs, start=1):
        output.append(
            f"{i}. {song['title']} by {song['artist']} | "
            f"Energy: {song['energy']} | Duration: {song['duration']} min"
        )
    return "\n".join(output)


def merge(left, right, key, steps):
    """Merge two sorted lists while recording steps."""
    merged = []
    i = 0
    j = 0

    steps.append(
        f"Merging:\nLeft: {format_playlist(left)}\n\nRight: {format_playlist(right)}\n"
    )

    while i < len(left) and j < len(right):
        steps.append(
            f"Comparing '{left[i]['title']}' ({left[i][key]}) "
            f"with '{right[j]['title']}' ({right[j][key]})"
        )

        if left[i][key] <= right[j][key]:
            merged.append(left[i])
            steps.append(f"Added '{left[i]['title']}' to merged list.")
            i += 1
        else:
            merged.append(right[j])
            steps.append(f"Added '{right[j]['title']}' to merged list.")
            j += 1

    while i < len(left):
        merged.append(left[i])
        steps.append(f"Added remaining '{left[i]['title']}' from left.")
        i += 1

    while j < len(right):
        merged.append(right[j])
        steps.append(f"Added remaining '{right[j]['title']}' from right.")
        j += 1

    steps.append(f"Merged result:\n{format_playlist(merged)}\n")
    return merged


def merge_sort(songs, key, steps):
    """Sort the playlist using merge sort."""
    if len(songs) <= 1:
        return songs

    mid = len(songs) // 2
    left_half = merge_sort(songs[:mid], key, steps)
    right_half = merge_sort(songs[mid:], key, steps)

    return merge(left_half, right_half, key, steps)


def sort_playlist(text, sort_key):
    """Main function used by Gradio."""
    try:
        songs = parse_playlist(text)

        if not songs:
            return "No songs entered.", "", ""

        original = format_playlist(songs)

        steps = []
        sorted_songs = merge_sort(songs, sort_key, steps)

        sorted_output = format_playlist(sorted_songs)
        step_output = "\n\n".join(steps)

        return original, sorted_output, step_output

    except Exception as e:
        return f"Error: {str(e)}", "", ""


example_input = """Blinding Lights, The Weeknd, 85, 3.2
Someone Like You, Adele, 40, 4.5
Levitating, Dua Lipa, 78, 3.4
Drivers License, Olivia Rodrigo, 35, 4.0
Stay, The Kid LAROI, 90, 2.4"""


with gr.Blocks() as demo:
    gr.Markdown("# Playlist Vibe Builder")
    gr.Markdown(
        "Enter songs in this format:\n"
        "`title, artist, energy, duration`\n\n"
        "Then choose whether to sort by energy or duration."
    )

    playlist_input = gr.Textbox(
        label="Playlist Input",
        lines=10,
        value=example_input
    )

    sort_key = gr.Dropdown(
        choices=["energy", "duration"],
        value="energy",
        label="Sort By"
    )

    sort_button = gr.Button("Sort Playlist")

    original_output = gr.Textbox(label="Original Playlist", lines=10)
    sorted_output = gr.Textbox(label="Sorted Playlist", lines=10)
    steps_output = gr.Textbox(label="Merge Sort Steps", lines=20)

    sort_button.click(
        fn=sort_playlist,
        inputs=[playlist_input, sort_key],
        outputs=[original_output, sorted_output, steps_output]
    )

demo.launch()
