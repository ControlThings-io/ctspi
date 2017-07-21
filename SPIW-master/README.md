# SPIW

I put these scripts together for pushing an X.509 certificate to the SPI EEPROM that you used for Justin Searle's Assessing and Exploiting Control Systems class. It is the same certificate pulled from the on disk dump, so the lab would dovetail nicely.

So, these scripts are a total hack, and there is likely a better way to accomplish it. It uses an existing screen session to push commands to the bus pirate; on the Control Things platform, run your buspirate shortcut for the screen command and get a session, and leave it alone. In another terminal window, run the scripts here.

It was pretty interesting putting it together. The SPI chips used in the class selected do not allow you to write consecutively past the and of a page, and they wrap per page. I had to figure out how to write to different pages, which should be obvious if you look at the script. Additionally, the SPI EEPROM does not have any erase commands, so the only way to recover from a screw up is to write all 0xFF to all 4 pages... The script should do at least one page, but would be easy to modify for all 4.
