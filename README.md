# UberCarrot
Acts as an interface to CasperCG, provides a graphics operator the ability to fill in dynamic fields in a given Flash (or HTML?) graphic file

## Stuff that this needs to be able to do:
* Load Casper-generated Flash graphics templates
* Send arbitrary text strings to Casper in order to populate the graphics fields
* Some form of dynamic text-replacement?
    - Maybe that means a lookup table of sorts, which refers to a plugin that returns a text string on every refresh?
    - Like `{{clock}}` refers to a function `make_clock` which returns a string
* A plugin architecture of sorts - but only of the field-replacement variety (as above) for now...
* Look nice (for James).
* Ooh, maybe have a *preview window*!
    * Figure out a way to have Casper generate a second output for the preview window dynamically
    * Or maybe have a Flash player panel, and see if we can get data into the Flash player...
* Be able to save and recall graphics, pre-filled
    * Prepare graphics ahead of time, save them and load them back in when necessary
        * This could be done by saving Caspar Datasets :)
    * Number-based? As in a graphic and associated content could be assigned a given number
        * When the number is keyed in (numpad only?), the graphic + content is recalled together, pre-filled
        * **Let's be honest, we're basically appropriating features from Chyron Lyric here ;)**
* Shortcut keys - animate/de-animate?
