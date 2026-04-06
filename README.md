# Playlist Vibe Builder

## Chosen Problem

This app solves the Playlist Vibe Builder problem by sorting songs based on energy or duration. It helps users organize a playlist depending on the mood or length they want.

## Chosen Algorithm

I chose Merge Sort because it is efficient, reliable, and easy to visualize step by step. It works well for sorting a list of songs because the playlist can be split into smaller parts, sorted, and then merged back together.

## Demo

(Add screenshot, gif, or video here)

## Problem Breakdown & Computational Thinking

### Decomposition

- Read playlist input
- Convert each line into a song record
- Choose sorting key
- Apply merge sort
- Show sorted results and sorting steps

### Pattern Recognition

- The algorithm repeatedly splits the list into halves
- It repeatedly compares values from two smaller lists
- It repeatedly merges items back in sorted order

### Abstraction

- The app shows comparisons and merged results
- It does not show unnecessary low-level Python details
- The focus is on how songs move into order

### Algorithm Design

Input → playlist text and sorting key  
Process → parse data, run merge sort, record steps  
Output → original playlist, sorted playlist, and merge sort steps

### Flowchart

![Flowchart](images/flowchart.png)

## Steps to Run

1. Install Python
2. Install required library:
   pip install -r requirements.txt
3. Run:
   python app.py

## Hugging Face Link

(Add link here)

## Testing

- Tested normal playlist input
- Tested empty input
- Tested one song
- Tested duplicate values
- Tested invalid format
- Tested invalid numeric input

## Author & AI Acknowledgment

(Add your name and AI acknowledgment here)
