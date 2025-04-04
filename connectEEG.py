import pylsl
from pylsl import StreamInlet
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading

def update_bar_graph(frame, variable_value):
    #Updates a bar graph with a new variable value.  This function is used by the animation.
    #Args:
    #frame:  The frame number of the animation (automatically passed by FuncAnimation).
    #variable_value: A list containing the current value for the variable's strength.  Passed as a list because animation update function expects a mutable object (list or array) rather than a simple integer.
    #bar_width: The width of the bar.
    ax.cla()  # Clear the current axes
    ax.bar([0], variable_value, color="green", width=.8)  # Plot the single bar
    ax.set_title("Theta/Beta Ratio x 100")
    ax.set_xticks([])
    ax.set_ylim(0, 8) #Set Y limit dynamically based on the maximum observed value
    ax.text(0, variable_value[0] + (max(variable_value)*0.05), str(variable_value[0]), ha='center', va='bottom') #Dynamically position text

# Main execution block
if __name__ == "__main__":
    # Initialize the figure and axes
    # first resolve an EEG stream on the lab network
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

    variable_value = [0]  #Start as list, to allow modification

    def update_data():
        while True:
                chunk, timestamps = inlet.pull_chunk()
                if timestamps and chunk:  # Check if both chunk and timestamps are not empty
                    # Assuming you want to use the first channel of the first sample
                    # and that the chunk has at least one sample and channel
                    tbr = (chunk[0][1] / chunk[0][3] * 100)
                    variable_value[0] = tbr
    # Start the data update thread in the background
    threading.Thread(target=update_data, daemon=True).start()

    # Create the animation
    ani = animation.FuncAnimation(fig, update_bar_graph, fargs=(variable_value,), interval=10, cache_frame_data=False) #Important to reduce memory usage

    plt.show()
