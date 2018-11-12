from flask import Blueprint, render_template, request, after_this_request, g
from monolith.database import db, Run
from monolith.auth import current_user, login_required
from enum import Enum


#daniele: new dependencies added!


import matplotlib
#avoid usage of tkinter that led to severe compatibility issues in python3.7
matplotlib.use('agg')
import matplotlib.pyplot as plt


statistics = Blueprint('statistics', __name__)

PLOTS_DIRECTORY = "monolith/static"
PLOTS_HTML_DIRECTORY = "static"
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
    run_ids = []

    runner_id = current_user.id


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
                run_ids.append(run.id)
                if (run.average_heartrate != None):
                    average_heartrates.append(run.average_heartrate)

            #saving into lists completed, now let's get plotting!
            #need to save plots on disk before actually showing them in the page!
            #now let's just reverse the order so as to have the most recent on the right-hand side
            #reverse acts in place, no need to assign to a new variable!

            run_names_concatenated = concatenate_run_name_id(run_names, run_ids)
            run_names_concatenated.reverse()

            x_label = "Run Name"
            distance_plot_filename = create_plot(runner_id, run_names_concatenated, distances, x_label, "Distance (m)", "Distance (m)", 'distance', '#4B8DD6', 1)
            avg_speed_plot_filename = create_plot(runner_id, run_names_concatenated, average_speeds, x_label, "Average Speed (Km/h)", "Average Speed (Km/h)", 'average_speed', '#2ECC71', 2)
            avg_heartrate_plot_filename = create_plot(runner_id, run_names_concatenated, average_heartrates, x_label, "Heartrate (hrpm)", "Average Heartrate (hrpm)", 'average_heartrate', '#F59A53', 2)
            elapsed_times_plot_filename = create_plot(runner_id, run_names_concatenated, elapsed_times, x_label, "Duration time (s)", "Duration Time (s)", 'elapsed_time', '#E74C3C', 2)
            elevation_gain_filename = create_plot(runner_id, run_names_concatenated, total_elevation_gains, x_label, "Total Elevation Gain (m)", "Total Elevation Gain (m)", 'elevation_gain', '#9B59B6', 2)

        else:
            #user doesn't have any runs or has not connected the Strava account
            runs = None

            distance_plot_filename = None
            avg_speed_plot_filename = None
            avg_heartrate_plot_filename = None
            elapsed_times_plot_filename = None
            elevation_gain_filename = None



    return render_template("statistics.html", runs=runs, plots_html_directory=PLOTS_HTML_DIRECTORY, distance_plot_filename=distance_plot_filename,
        avg_speed_plot_filename=avg_speed_plot_filename, avg_heartrate_plot_filename=avg_heartrate_plot_filename,
        elapsed_times_plot_filename=elapsed_times_plot_filename, elevation_gain_filename=elevation_gain_filename,
        runner_id=runner_id)





#plot_type = 1 --> line plot
#          = 2 --> bar plot
def create_plot(runner_id, x_values, y_values, xlabel, ylabel, title, filename, color, plot_type):
    filename_output = None

    if  len(y_values) > 0:
        #reverse here as well!
        y_values.reverse()
        if plot_type == 1:
            plt.plot(x_values, y_values, color=color)
        elif plot_type == 2:
            plt.bar(x_values, y_values, color=color)

        filename_output = "plots/" + filename + "_" + str(runner_id) + PLOTS_FORMAT
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=90)
        plt.title(title)
        plt.savefig(PLOTS_DIRECTORY + "/" + filename_output, bbox_inches="tight")
        plt.close()

    return filename_output


#Used to distinguish runs with the same name
def concatenate_run_name_id(run_names, run_ids):
    run_names_concatenated = []
    for run_id, run_name in zip(run_ids, run_names):
        run_names_concatenated.append(str(run_id) + "_" + run_name)
    return run_names_concatenated


@statistics.after_request
def per_request_callbacks(response):
    for func in getattr(g, 'call_after_request', ()):
        response = func(response)
    return response


def invalidate_cache():
    @statistics.after_request
    def add_header(response):
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        response.headers["Cache-Control"] = "no-cache, no-store, must-validate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response

