# Simple weather (snow/rain) simulator using particles and UI practice, created during ASWF SLP '24 by Helena Xu

import maya.cmds as cmds

class WeatherSimulatorUI(object):
    def __init__(self):
        self.window_name = "WeatherSimulatorWindow"

    def show(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

        cmds.window(self.window_name, title="Weather Simulator")
        self.build_ui()
        cmds.showWindow(self.window_name)

    def build_ui(self):
        cmds.columnLayout(adjustableColumn=True)

        # Weather Type (only rain and snow for now)
        cmds.text(label="Select Weather Type:")
        self.weather_type_menu = cmds.optionMenu(label="Weather Type", changeCommand=self.update_particle_types)
        cmds.menuItem(label="Rain")
        cmds.menuItem(label="Snow")

        # Emitter Rate (play around with these, can change the falling effect of rain/snow)
        cmds.text(label="Emitter Rate:")
        self.rate_slider = cmds.optionMenu(label="Select Rate")
        cmds.menuItem(label="50")
        cmds.menuItem(label="100")
        cmds.menuItem(label="200")

        # Emitter Type
        self.emitter_type_label = cmds.text(label="Emitter Type:")
        self.emitter_type_menu = cmds.optionMenu(label="Select Emitter Type")

        # Particle Render Type
        cmds.text(label="Particle Render Type:")
        self.particle_type_menu = cmds.optionMenu(label="Select Particle Render Type")

        # Initialize with default particle types
        self.update_particle_types()

        # Buttons
        cmds.button(label="Apply Settings", command=self.apply_settings)
        cmds.button(label="Play Animation", command=self.play_animation)
        cmds.button(label="Stop Animation", command=self.stop_animation)
        cmds.button(label="Close", command=self.close)

    def update_particle_types(self, *args):
        # Clear the current particle type options
        cmds.optionMenu(self.particle_type_menu, edit=True, deleteAllItems=True)

        # Get the selected weather type
        weather_type = cmds.optionMenu(self.weather_type_menu, query=True, value=True)

        # Define particle types for each weather type (this ive played around for best mix and match settings)
        if weather_type == "Rain":
            particle_types = ["Points", "Sprites", "Streak"]
            emitter_types = ["Omni", "Distributed", "Volume"]
            cmds.text(self.emitter_type_label, edit=True, visible=True)
            cmds.optionMenu(self.emitter_type_menu, edit=True, visible=True)
        elif weather_type == "Snow":
            particle_types = ["Multipoint", "Multistreak", "Cloud"]
            emitter_types = ["Distributed"]
            cmds.text(self.emitter_type_label, edit=True, visible=False)
            cmds.optionMenu(self.emitter_type_menu, edit=True, visible=False)

        # Add the appropriate particle types to the menu since I have separate settings for rain/snow
        for pt in particle_types:
            cmds.menuItem(label=pt, parent=self.particle_type_menu)

        # Add emitter types
        cmds.optionMenu(self.emitter_type_menu, edit=True, deleteAllItems=True)
        for et in emitter_types:
            cmds.menuItem(label=et, parent=self.emitter_type_menu)

    def apply_settings(self, *args):
        # Clear the scene
        cmds.file(new=True, force=True)

        # Create a ground plane
        plane = cmds.polyPlane(width=25, height=25)[0]
        cmds.setAttr(plane + ".translateY", 0)

        # Get settings from user
        weather_type = cmds.optionMenu(self.weather_type_menu, query=True, value=True)
        rate = int(cmds.optionMenu(self.rate_slider, query=True, value=True)) if cmds.optionMenu(self.rate_slider, query=True, visible=True) else 0
        emitter_type = cmds.optionMenu(self.emitter_type_menu, query=True, value=True) if cmds.optionMenu(self.emitter_type_menu, query=True, visible=True) else "Omni"
        particle_render_type_label = cmds.optionMenu(self.particle_type_menu, query=True, value=True)

        # Convert particle render type label to integer (played around with echoing the commands in script so I could find each index associated to which particle render type)
        particle_render_type_dict = {
            "Multipoint": 0,
            "Multistreak": 1,
            "Numeric": 2,
            "Points": 3,
            "Spheres": 4,
            "Sprites": 5,
            "Streak": 6,
            "Blobby Surface": 7,
            "Cloud": 8
        }
        particle_render_type = particle_render_type_dict.get(particle_render_type_label, 0)

        # Create selected weather effect
        if weather_type == "Rain":
            self.create_rain(rate, emitter_type, particle_render_type)
        elif weather_type == "Snow":
            self.create_snow(rate, emitter_type, particle_render_type)

        # Set the timeline to 50 frames (also played with this for best setting)
        cmds.playbackOptions(minTime=0, maxTime=50)

    def create_rain(self, rate, emitter_type, particle_render_type):
        # Create an emitter and particle system
        emitter = cmds.emitter(type='omni', rate=rate, speed=1) # Set as omni for default initialization but can change below
        particles = cmds.particle()

        # Set emitter type
        emitter_type_dict = {"Omni": 0, "Distributed": 1, "Volume": 4}
        cmds.setAttr(emitter[1] + ".emitterType", emitter_type_dict.get(emitter_type, 0))

        # Position the emitter above the scene
        cmds.setAttr(emitter[0] + ".translateY", 20)
        cmds.setAttr(emitter[0] + ".translateX", 0)
        cmds.setAttr(emitter[0] + ".translateZ", 0)

        # Connect the emitter to the particle system
        cmds.connectDynamic(particles[0], em=emitter)

        # Set particle render type
        cmds.setAttr(particles[1] + ".particleRenderType", particle_render_type)

        # Special case: rain with sprites (if I didn't have this it looks weird/off so edge case)
        if particle_render_type == 5:  # Sprites
            cmds.setAttr(particles[1] + ".aiMaxParticleRadius", 2)
            cmds.setAttr(particles[1] + ".aiRadiusMultiplier", 0.1)

        # Add a gravity field to pull particles down
        gravity = cmds.gravity()
        cmds.connectDynamic(particles[0], f=gravity)

        # Make particles collide with the plane
        cmds.collision("pPlane1", particles[0])

    def create_snow(self, rate, particle_render_type):
        # Create a snow particle system
        emitter = cmds.emitter(type='omni', rate=rate, speed=3)
        particles = cmds.particle()

        # For snow, set default to be distrubuted
        cmds.setAttr(emitter[1] + ".emitterType", 1)  # Distributed

        # Position the emitter above the scene
        cmds.setAttr(emitter[0] + ".translateY", 20)
        cmds.setAttr(emitter[0] + ".translateX", 0)
        cmds.setAttr(emitter[0] + ".translateZ", 0)

        # Connect the emitter to the particle system
        cmds.connectDynamic(particles[0], em=emitter)

        # Set particle render type based on user selection for snow
        cmds.setAttr(particles[1] + ".particleRenderType", particle_render_type)

        # Add a gravity field to pull particles down
        gravity = cmds.gravity(magnitude=9)
        cmds.connectDynamic(particles[0], f=gravity)

        # Make particles collide with the plane
        cmds.collision("pPlane1", particles[0])

    def play_animation(self, *args):
        cmds.play(forward=True)

    def stop_animation(self, *args):
        cmds.play(state=False)

    def close(self, *args):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

# Create and show the UI
ui = WeatherSimulatorUI()
ui.show()
