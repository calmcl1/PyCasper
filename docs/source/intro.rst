====================
All About UberCarrot
====================

UberCarrot *(working title)* is an interface that allows a user to use a `CasparCG Server <http://casparcg.com>`_ as a :term:`graphics machine<character generator>` or :term:`character generator`.

This mostly happens by using Caspar/SVT AMCP commands over a TCP socket and working with Caspar Template and Dataset concepts.

Using UberCarrot
================

For example, the process of taking a graphic (let's say a lower third) on air might be:
    #. Open the graphic template (located on the CasparCG server) in UberCarrot.
    #. The template will contain text fields that we can fill in. Use the text boxes in UberCarrot to fill these in.7
    #. Click the *Animate* button on the UberCarrot window. This will instruct CasparCG to take the graphic to air.
    #. When we want the graphic to disappear from the output, clicking the *De-animate* button will instruct CasparCG to let the Flash template to play through the last section of its animation, which typically takes the graphic off the screen.

However, if we want, we can create the graphic ahead of time, and save it. Later, when we need it, we can recall the graphic (including the contents of the text-boxes) and play it out. **Beware:** this workflow is not even close to confirmed, and may change later.
    #. Choose a unique numeric ID (1-9999) for the graphic that you want to create. Type it in using the **numpad**. Press :kbd:`Enter`.
    #. Open the graphic template as above.
    #. Fill in the fields provided.
    #. Go to File -> Save, or, press :kbd:`Ctrl-S`. The graphic (with associated text) has now been assigned to the ID number you chose.
    #. When you want to recall the graphic, use the numpad to type the ID number and press :kbd:`Enter`.
    #. Animate and de-animate the graphic as normal.