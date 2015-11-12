# UberCarrot
Acts as an interface to CasperCG, provides a graphics operator the ability to fill in dynamic fields in a given Flash graphic file

## Stuff that this needs to be able to do:
* Load Casper-generated Flash graphics templates
* Send arbitrary text strings to Casper in order to populate the graphics fields
* Some form of dynamic text-replacement?
    - Maybe that means a lookup table of sorts, which refers to a plugin that returns a text string on every refresh?
    - Like `{{clock}}` refers to a function `make_clock` which returns a string
* A plugin architecture of sorts - but only of the field-replacement variety (as above) for now...
* Look nice (for James).