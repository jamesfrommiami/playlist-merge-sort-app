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

### Test 1: Normal input
- Input: multiple songs with different energy values  
- Expected: songs sorted correctly by chosen key  
- Result: worked as expected  

### Test 2: Empty input
- Input: no songs entered  
- Expected: error message or empty output  
- Result: displayed "No songs entered"  

### Test 3: One song
- Input: single song  
- Expected: same song returned  
- Result: worked as expected  

### Test 4: Duplicate values
- Input: songs with same energy  
- Expected: sorted correctly, duplicates handled  
- Result: worked as expected  

### Test 5: Invalid format
- Input: missing values in a line  
- Expected: error message  
- Result: error message displayed  

### Test 6: Invalid numeric input
- Input: energy as text instead of number  
- Expected: error message  
- Result: error message displayed  

## Author & AI Acknowledgment

(Add your name and AI acknowledgment here)
