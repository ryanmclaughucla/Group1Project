import pylsl
from pylsl import StreamInlet
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import os
import csv

file_path = "C:/Users/Ryan/Desktop/OpenBCI1.csv"

def update_bar_graph(frame, variable_value):
    #Updates a bar graph with a new variable value.  This function is used by the animation.
    ax.cla()  # Clear the current axes
    ax.bar([0], variable_value, color="green", width=.8)  # Plot the single bar
    ax.set_title("Theta/Beta Ratio x 100")
    ax.set_xticks([])
    ax.set_ylim(0, 8) #Set Y limit dynamically based on the maximum observed value
    ax.text(0, variable_value[0] + (max(variable_value)*0.05), str(variable_value[0]), ha='center', va='bottom') #Dynamically position text

def update_data():
    while True:
        chunks, timestamps = inlet.pull_chunk()
        if timestamps and chunks[0][0]==0: # Check if both chunk and timestamps are not empty
            tbrt = 0
            for chunk in chunks:
                if chunk[0] == (9 or 7 or 8):
                        tbri = (chunk[2] / chunk[4] * 100)
                        tbrt += tbri
            if tbrt != 0:
                variable_value[0] = tbrt/4
                data = [timestamps[0],variable_value[0]]
                with open(file_path, "a+", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow (data)


print("looking for an EEG stream...")
streams = pylsl.resolve_streams()
stream = streams[0]
# create a new inlet to read from the stream
inlet = StreamInlet(stream)
fig, ax = plt.subplots()
fig.set_facecolor("white")
# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
variable_value = [0]

##def ani():
  ##  animation.FuncAnimation(fig, update_bar_graph, fargs=(variable_value,), interval=10, cache_frame_data=False)



def cleardata():
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow (["Time","TBR"])
    variable_value = [0]

if __name__ == "__main__":
    # Start the data update thread in the background
    threading.Thread(target=update_data, daemon=True).start()
    plt.show()
