from flask import Blueprint, render_template, request
from monolith.database import db, Run
from monolith.auth import current_user, login_required
from enum import Enum

#daniele: new dependencies added!


import matplotlib
#avoid usage of tkinter that led to severe compatibility issues in python3.7
matplotlib.use('agg')
import matplotlib.pyplot as plt


statistics = Blueprint('statistics', __name__)

PLOTS_DIRECTORY = "static"
PLOTS_FORMAT = ".png"




@statistics.route('/statistics', methods=['GET'])
@login_required
def stats():
    #plotted on the x axis
    starting_dates = []
    run_names = []

    #plotted on the y axis
    distances = []
    average_speeds = []
    average_heartrates = []
    total_elevation_gains = []
    elapsed_times = []

    #get statistics of all runs of current user
    if current_user is not None and hasattr(current_user, 'id'):
        runs = db.session.query(Run).filter(Run.runner_id == current_user.id)
        if runs.count():
            #now save all the attributes to the corresponding arrays
            for run in runs:
                distances.append(run.distance)
                starting_dates.append(run.start_date)
                average_speeds.append(run.average_speed)
                total_elevation_gains.append(run.total_elevation_gain)
                elapsed_times.append(run.elapsed_time)
                run_names.append(run.name)
                if(run.average_heartrate != None):
                    average_heartrates.append(run.average_heartrate)
                #saving into lists completed, now let's get plotting!
                #need to save plots on disk before actually showing them in the page!

                x_label = "Run Name"
                distance_plot_filename = create_plot(run_names, distances, x_label, "Distance (m)", "Distance of your last 10 runs", 'distance', 'blue', 1)
                avg_speed_plot_filename = create_plot(run_names, average_speeds, x_label, "Average Speed (Km/h)", "Average speed of your last 10 runs", 'average_speed', 'g', 2)
                avg_heartrate_plot_filename = create_plot(run_names, average_heartrates, x_label, "Heartrate (hrpm)", "Average Heartrate of your last 10 runs", 'average_heartrate', 'orange', 2)
                elapsed_times_plot_filename = create_plot(run_names, elapsed_times, x_label, "Elapsed time (s)", "Duration time of your last 10 runss", 'elapsed_time', 'red', 2)
                elevation_gain_filename = create_plot(run_names, total_elevation_gains, x_label, "Total Elevation Gain (m)", "Total elevation gain of your last 10 runs", 'elevation_gain', 'brown', 2)

        else:
            #user doesn't have any runs or has not connected the Strava account
            runs = None

            distance_plot_filename = None
            avg_speed_plot_filename = None
            avg_heartrate_plot_filename = None
            elapsed_times_plot_filename = None
            elevation_gain_filename = None

    return render_template("statistics.html", runs=runs, plots_directory=PLOTS_DIRECTORY, distance_plot_filename=distance_plot_filename,
        avg_speed_plot_filename=avg_speed_plot_filename, avg_heartrate_plot_filename=avg_heartrate_plot_filename,
        elapsed_times_plot_filename=elapsed_times_plot_filename, elevation_gain_filename=elevation_gain_filename )



#plot_type = 1 --> line plot
#          = 2 --> bar plot
def create_plot(x_values, y_values, xlabel, ylabel, title, filename, color, plot_type):
    filename_output = None

    if len(y_values) > 0:
        if plot_type == 1:
            plt.plot(x_values, y_values, color=color)
        elif plot_type == 2:
            plt.bar(x_values, y_values, color=color)

        filename_output = "plots/" + filename + PLOTS_FORMAT
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.savefig(PLOTS_DIRECTORY + "/" + filename_output)
        plt.close()

    return filename_output


