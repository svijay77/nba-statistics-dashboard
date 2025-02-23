from pathlib import Path
import json
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import shiny
from shiny import App, reactive
from shiny.ui import input_dark_mode, page_fluid, input_slider, panel_title, page_output, markdown, layout_sidebar, input_selectize, output_text, input_date_range, input_radio_buttons, output_ui, output_plot, output_table, panel_sidebar, panel_main, navset_card_tab, nav_panel, input_checkbox_group
from shinywidgets import output_widget, render_widget

df = pd.read_csv("data/data.csv")

# Define the UI layout
ui = page_fluid(
        input_dark_mode(),
        panel_title("NBA Player Statistics Dashboard", "NBA Player Statistics Dashboard"),
        layout_sidebar(
            panel_sidebar(
                input_selectize(id="team", label="Team", choices=list(df['Tm'].unique()), selected="LAL"),

                
                input_radio_buttons(id="stat", label="Statistic", choices={
                    "PTS": "PTS", 
                    "AST": "AST", 
                    "TRB": "TRB", 
                    "BLK": "BLK", 
                    "STL": "STL"
                }, selected="PTS"),

                output_ui("plot_stats"),

                input_checkbox_group(id="region", label="NBA Team Region", choices={
                    "Atlantic": "Atlantic",
                    "Central": "Central",
                    "Southeast": "Southeast",
                    "Northwest": "Northwest",
                    "Pacific": "Pacific",
                    "Southwest": "Southwest"
                })
            ),
            panel_main(

                navset_card_tab(
                    nav_panel("Player Stats", 
                                output_plot("stats_plot", width='100%', height='700px'),
                                output_table("player_stats_table")
                            ),
                    nav_panel("About",
                            markdown("This dashboard displays NBA player statistics per game for the 2023-2024 season. You can select a team, choose a statistic among points, assists, rebounds, blocks, and steals, filter players by minimum and maximum values, and view these statistics by team. You can also filter the bottom plot by NBA Team Region to select different groups of teams. There is a table at the bottom to view player statistics in more detail.")),
                ),
                page_output("sidebar"),
                page_output("plots"),
                )
            )
    )

# Define the server function
def server(input, output, session):
    def get_stats_range():
        stats = ['PTS', 'AST', 'TRB', 'BLK', 'STL']
        ranges = []
        for stat in stats:
            min_stat = df[stat].min()
            max_stat = df[stat].max()

            ranges.append((min_stat, max_stat))
        return ranges
    
    @output
    @shiny.render.ui
    def plot_stats():
        pts_range, ast_range, trb_range, blk_range, stl_range = get_stats_range()
        if input.stat() == 'PTS':
            values = (pts_range[0], pts_range[1], 1, ((pts_range[0] + pts_range[1]) / 2))
        elif input.stat() == 'AST':
            values = (ast_range[0], ast_range[1], 1, ((ast_range[0] + ast_range[1]) / 2))
        elif input.stat() == 'TRB':
            values = (trb_range[0], trb_range[1], 1, ((trb_range[0] + trb_range[1]) / 2))
        elif input.stat() == 'BLK':
            values = (blk_range[0], blk_range[1], 1, ((blk_range[0] + blk_range[1]) / 2))
        elif input.stat() == 'STL':
            values = (stl_range[0], stl_range[1], 1, ((stl_range[0] + stl_range[1]) / 2))


        return input_slider("plot_stats", "Statistic Range", values[0], values[1], (values[2], values[3]))
    
    @shiny.render.plot
    def stats_plot():
        team = input.team()
        selected_stat = input.stat()
        regions = input.region()
        min_stat, max_stat = input.plot_stats()

        filtered_df = df[(df['Tm'] == team)]
        filtered_df = filtered_df[(filtered_df[selected_stat] >= min_stat) & (filtered_df[selected_stat] <= max_stat)]

        fig, ax = plt.subplots(2, 1, figsize=(10, 5))

        team_stat = filtered_df[selected_stat]

        ax[0].bar(filtered_df["Player"], team_stat, label=selected_stat)

        ax[0].set_xticklabels(filtered_df["Player"], rotation=90, ha='center')    
        ax[0].set_xlabel(f"Players on {team}")    
        ax[0].set_ylabel(selected_stat)
        ax[0].legend()

        region_dict = {
            "Atlantic": ["BOS", "BKN", "NYK", "PHI", "TOR"],
            "Central": ["CHI", "CLE", "DET", "IND", "MIL"],
            "Southeast": ["ATL", "CHA", "MIA", "ORL", "WAS"],
            "Northwest": ["DEN", "MIN", "OKC", "POR", "UTA"],
            "Pacific": ["GSW", "LAC", "LAL", "PHO", "SAC"],
            "Southwest": ["DAL", "HOU", "MEM", "NOP", "SAS"]
        }
        teams = []
        for region in regions:
            teams += region_dict[region]
        print(teams)
        
        grouped = df[["PTS", "AST", "BLK", "STL", "TRB", "Tm"]].groupby("Tm").mean().reset_index()
        selected_regions = grouped[grouped["Tm"].isin(teams)]
        print("i get past here")
        team_statg = selected_regions[selected_stat]

        ax[1].bar(selected_regions["Tm"], team_statg, label=selected_stat)

        ax[1].set_xticklabels(selected_regions["Tm"], rotation=90, ha='center')        
        ax[1].set_xlabel("Teams")
        ax[1].set_ylabel(selected_stat)
        ax[1].legend()

        plt.tight_layout()

        return fig

    @output
    @shiny.render.table
    def player_stats_table():
        team = input.team()
        selected_stat = input.stat()
        min_stat, max_stat = input.plot_stats()

        filtered_df = df[(df['Tm'] == team)]
        filtered_df = filtered_df[(filtered_df[selected_stat] >= min_stat) & (filtered_df[selected_stat] <= max_stat)]
        return pd.DataFrame(filtered_df[['Player', 'PTS', 'AST', 'TRB', 'BLK', 'STL', ]])

app = App(ui, server)

if __name__ == "__main__":
    app.run()