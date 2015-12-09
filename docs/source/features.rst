What Can UberCarrot Do?
======================

Ultimately, at the moment: *not much*.

It's fair to say that this is still very much a work-in progress, and in the **alpha** stage of it's lifecycle.

However, UC aspires to grand things! Here's what we *intend* to do (at the current stage):

* Load CCG-generated Flash graphics templates
    * Possibly some kind of media manager/template manager, to explore the contents of the Caspar server?
* Send arbitrary text strings to CCG in order to populate the graphics fields
* Some form of dynamic text replacement?
    * Maybe that means a lookup table of sorts, which refers to a plugin that returns a text string on every refresh?
    * Like ``{{clock}}`` refers to a function ``make_clock`` which returns a string
* A plugin architecture of sorts - but only of the field-replacement variety (as above) for now...
* Ooh, maybe have a *preview window*!
    * Figure out a way to have CCG generate a second output for the preview window dynamically
    * Or maybe have a Flash player panel, and see if we can get data into the Flash player...
* Be able to save and recall graphics, pre-filled
    * Prepare graphics ahead of time, save them and load them back in when necessary
        * This could be done by saving Caspar Datasets :)
* Shortcut keys - animate/de-animate?
* Is it in the remit of UC to be able to configure CCG?
* Graphics shotbox?
* Look pleasant
