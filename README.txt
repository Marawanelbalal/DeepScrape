User manual for DeepScrape

(Please read the whole file before opening the program)

DeepScrape is an eBay web scraping tool designed for dynamic data collection and analysis

Please make sure to download all requirements in requirements.txt before trying to run the program.

You can run this command in the terminal to download all dependencies:
pip install -r requirements.txt

1- Before running the program, go to GUI.py and run that file, don't be discouraged if it takes a long time.

2- To skip the intro animation, press Enter and the main menu will show up after 3 seconds

3- To start scraping, enter a query in the long bar at the top, on the left bar enter (items per request)
The recommended items per request is 50, but the user may enter up to 200 if they choose to.
Enter the maximum number of items in the right bar, the application will keep sending requests till it reaches that number or slightly above it.

4- Wait for the product cards to appear, once they do that is the indication that the items are loaded in

5- Start analyzing by picking an analysis type and pressing the analyze button, a figure will appear to indicate the end of the function
For very specific details about the workings of the function, the user should read the terminal logs, the GUI will not display very specific details
like betweenness centrality or degree.

6- It is best to close the figure before opening another one with another analysis type, all analysis types show some type of figure.

7- Be careful of (Product Network Analysis) option, that option uses selenium so it is best to pick 20 items or lower for it
Even with 20 items, the function might have a runtime of 2-3 minutes, the user can of course choose to use a big number like 50,
but the user will have to wait a longer time.

8- Multiregional heatmap and review analysis are also on the heavier side of functions since they involve requests and bs4,
but compared to selenium they are very light

9- Currently error detection in this program is kept to a minimum, so please do not enter characters where integers are required
and do not leave data fields empty. Though, most of the time it is not an issue.

10- Please do not maximize or interact heavily with matplotlib figures, this overloads and possibly hijacks the main GUI thread
and causes a crash everytime. Only close the figure after you are done viewing it

11. If an analysis function ever errors out, simply close the program and reopen it and retry. Heavy analysis (network graph, 3D plot, multi-regional heatmap) can sometimes overload the GUI thread.

Happy scraping!
