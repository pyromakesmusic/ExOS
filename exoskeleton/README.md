# ExOS

Hello! This is the documentation for the ExOS exoskeleton operating system.

It contains as an internal dependency, **pyonics**, another package meant
to be useful for bionics problems in general.

## Overview

## Robot Files
Files included may be in .ROB format (Klamp't native) or in URDF (Universal Robot Definition Format), but both contain nearly the same information.

## Interface

The included interface module contains several built-in components.

### Heads-Up Displays

The **AugmentOverlayUI** class provides options for creating a simple HUD in one user-selectable color.
Future plans involve dynamically updating color depending on the input of the camera and ambient light levels.

## Applications
The provided files for ExOS contain a minimal set of applications, the goal of which is to 
be useful in a rescue context. Initially, we'll be developing basic PDA-level apps: clock, calendar, notes, and so forth.

With feedback and as the infrastructure gets built out, we will look into more high-level and specialized applications.

### Global Positioning (GPS)

The **ExOS** class is built with GPS integration by default.

## pyonics

More information can be found in the **pyonics** subfolder, as it is mean to function
as a standalone library.

This is the intended destination of the "Muscle" class.