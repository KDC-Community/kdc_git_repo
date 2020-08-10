# Advanced Emulator Launcher #

Multi-emulator front-end and general application launcher for Kodi. Includes offline scrapers for 
MAME and No-Intro ROM sets and also supports scrapping ROM metadata and artwork online. 
ROM auditing for No-Intro ROMs using No-Intro or Redump XML DAT files. Launching of games 
and standalone applications is also available.

### Kodi forum thread ###

More information and discussion about AEL can be found in the [Advanced Emulator Launcher thread] 
in the Kodi forum.

[Advanced Emulator Launcher thread]: https://forum.kodi.tv/showthread.php?tid=287826

### Documentation ###

A User's Guide, some tutorials and guides to configure emulators can be found in 
the [Advanced Emulator Launcher Wiki].

[Advanced Emulator Launcher Wiki]: https://github.com/Wintermute0110/plugin.program.advanced.emulator.launcher/wiki

## Installing the latest released version ##

Follow [this link](https://github.com/Wintermute0110/repository.wintermute0110/tree/master/plugin.program.advanced.emulator.launcher) 
and download the ZIP file of the version you want. Use this ZIP file to install the addon in Kodi.

## Installing the latest development version ##

It is important that you follow this instructions or Advanced Emulator Launcher won't work well.

  1) In this page click on the green button `Clone or Download` --> `Download ZIP`

  2) Uncompress this ZIP file. This will create a folder named `plugin.program.advanced.emulator.launcher-master`

  3) Rename that folder to `plugin.program.advanced.emulator.launcher`

  4) Compress that folder again into a ZIP file. 

  5) In Kodi, use that ZIP file (and not the original one) to install the plugin in `System` --> `Addons` 
     --> `Install from ZIP file`.

  6) You are done!
  
  
  or


* [Download the Ctrl_Esc_REPO Version](https://bit.ly/3klU2b7)

and take a look at the confic and bios files!





------------------------------------------------------------------------------------------------------------------------



# Advanced Emulator Launcher metadata and artwork data model #

 * Look in [Pydocs_setInfo] for valid setInfo() infoLabels.

 * Look in [Pydocs_setArt] for valid setArt() infoLabels.

 * Look in [Pydocs_setProperty] for valid setProperty() infoLabels.
 
 * Look in [Kodi_wiki_artwork] for supported Kodi artwork.
 
[Pydocs_setInfo]: http://mirrors.xbmc.org/docs/python-docs/16.x-jarvis/xbmcgui.html#ListItem-setInfo
[Pydocs_setArt]: http://mirrors.xbmc.org/docs/python-docs/16.x-jarvis/xbmcgui.html#ListItem-setArt
[Pydocs_setProperty]: http://mirrors.xbmc.org/docs/python-docs/16.x-jarvis/xbmcgui.html#ListItem-setProperty
[Kodi_wiki_artwork]: http://kodi.wiki/view/InfoLabels#Images_Available_in_Kodi


## Category metadata labels ##

 Metadata name | AEL name  | setInfo label | Type                 |
---------------|-----------|---------------|----------------------|
 Title         | m_name    | title         | string               |
 Genre         | m_genre   | genre         | string               |
 Plot          | m_plot    | plot          | string               |
 Rating        | m_rating  | rating        | string range 0 to 10 |
 Trailer       | s_trailer | trailer       | string               |
               |           | overlay       | int range 0 to 8     |

 * setInfo first argument is `video`. 


## Categories asset labels ##
 
 Asset name  | AEL name    | setArt label | setInfo label |
-------------|-------------|--------------|---------------|
 Thumb       | s_thumb     | thumb        |               |
 Fanart      | s_fanart    | fanart       |               |
 Banner      | s_banner    | banner       |               |
 Flyer       | s_flyer     | poster       |               |
 Trailer     | s_trailer   |              | trailer       |
 Extrafanart | extrafanart | extrafanart1 |               |
 Extrafanart | extrafanart | extrafanart2 |               |

 * `thumb` = `DefaultFolder.png` is the default for categories.

 * Trailer is an asset, however label is set with `setInfo()` instead of `setArt()`.

 * Do not set any artwork in the ListItem constructor, only with setArt().

 * `extrafanart` is a Python list.

## Launcher metadata labels ##

 Metadata name | AEL name  | setInfo | setProperty | Type                 |
---------------|-----------|---------|-------------|----------------------|
 Title         | m_name    | title   |             | string               |
 Year          | m_year    | year    |             | string               |
 Genre         | m_genre   | genre   |             | string               |
 Plot          | m_plot    | plot    |             | string               |
 Studio        | m_studio  | studio  |             | string               |
 Rating        | m_rating  | rating  |             | string range 0 to 10 |
 Trailer       | s_trailer | trailer |             | string               |
 Platform      | platform  |         | platform    | string               |
               |           | overlay |             | int range 0 to 8     |

 * `setInfo()` first argument is `video`. 
 
 * AEL platform uses an internal "official" list for the scrapers to work properly. 
   Platform is never read from NFO files. Also, AEL platform is a Launcher property, 
   not a ROM property.

 * Year and Rating are integers according to Kodi Pydocs. However, they are stored as string. 
   If Year and Rating are not set they are the empty strings, which is different from integer 0. 
   Kodi seems to handle this behaviour well.


## Launchers asset labels ##
 
 Asset name  | AEL name    | setArt label | setInfo label |
-------------|-------------|--------------|---------------|
 Thumb       | s_thumb     | thumb        |               |
 Fanart      | s_fanart    | fanart       |               |
 Banner      | s_banner    | banner       |               |
 Flyer       | s_flyer     | poster       |               |
 Trailer     | s_trailer   |              | trailer       |
 Extrafanart | extrafanart | extrafanart1 |               |
 Extrafanart | extrafanart | extrafanart2 |               |

 * `thumb` label is set to `DefaultProgram.png` or `DefaultFolder.png`.

 * Trailer is an asset, however label is set with `setInfo()` instead of `setArt()`.

 * `extrafanart` is a Python list.

## ROMs metadata labels ##

 Metadata name | AEL name  | setInfo | setProperty | Type                 |
---------------|-----------|---------|-------------|----------------------|
 Title         | m_name    | title   |             | string               |
 Year          | m_year    | year    |             | string               |
 Genre         | m_genre   | genre   |             | string               |
 Plot          | m_plot    | plot    |             | string               |
 Studio        | m_studio  | studio  |             | string               |
 Rating        | m_rating  | rating  |             | string range 0 to 10 |
 Trailer       | s_trailer | trailer |             | string               |
 Platform      | platform  |         | platform    | string               |
               |           | overlay |             | int range 0 to 8     |

 * setInfo first argument is `video`. 

 * Platform is a launcher property, not a ROM property. Also, `setProperty()` is used instead 
   of `setInfo()`.

 * Year and Rating are integers according to Kodi Pydocs. However, they are stored as string. 
   If Year and Rating are not set they are the empty strings, which is different from integer 0. 
   Kodi seems to handle this behaviour well.


## ROMs asset labels ##
 
 Asset name  | AEL name    | setArt label | setInfo label | MAME mapping for MAME views |
-------------|-------------|--------------|---------------|-----------------------------|
 Title       | s_title     | title/thumb  |               | title                       |
 Snap        | s_snap      | snap         |               | snap                        |
 Fanart      | s_fanart    | fanart       |               | fanart                      |
 Banner      | s_banner    | banner       |               | marquee                     |
 Clearlogo   | s_clearlogo | clearlogo    |               | clearlogo                   |
 Boxfront    | s_boxfront  | boxfront     |               | cabinet                     |
 Boxback     | s_boxback   | boxback      |               | cpanel                      |
 Cartridge   | s_cartridge | cartridge    |               | pcb                         |
 Flyer       | s_flyer     | poster       |               | flyer                       |
 Map         | s_map       | map          |               |                             |
 Manual      | s_manual    |              |               | manual                      |
 Trailer     | s_trailer   |              | trailer       | trailer                     |
 Extrafanart | extrafanart | extrafanart1 |               | extrafanart                 |
 Extrafanart | extrafanart | extrafanart2 |               | extrafanart                 |
 
 * `thumb` label is set to `DefaultProgram.png`.

 * For Confluence/Estuary, user will be able to configure what artwork will be set as `thumb`
   and `fanart`. 

 * Trailer is an asset, however label is set with setInfo() instead of setArt()

 * `extrafanart` is a Python list.

## Launchers/Categories artwork supported by plugins ##

 Plugin | Thumb | Fanart | Banner | Poster | Trailer |
--------|-------|--------|--------|--------|---------|
AL      |  YES  |  YES   |  NO    |  NO    | NO      |
AEL     |  YES  |  YES   |  YES   |  YES   | YES     |
HL      |  YES  |  YES   |  YES   |  YES   | ???     |
IARL    |  ???  |  ???   |  ???   |  ???   | ???     |


## Console ROMs asset availability ##

  Artwork site    | Title | Snap | Fanart | Banner | Boxfront | Boxback | Cartridge | Flyer | Map | Manual | Trailer |
------------------|-------|------|--------|--------|----------|---------|-----------|-------|-----|--------|---------|
[EmuMovies]       |  YES  | YES  |  NO    |   NO   |   YES    |   YES   |    YES    |  YES  | YES |  YES   |   YES   |
[HyperSpin Media] |  NO   | NO   |  <1>   |   YES  |   YES    |   NO    |    YES    |  <1>  | <1> |  NO    |   NO    |
[No-Intro]        |  YES  | NO   |  NO    |   NO   |   YES    |   YES   |    YES    |  NO   | NO  |  YES   |   NO    |
[Retroarch]       |  YES  | YES  |  NO    |   NO   |   YES    |   NO    |    NO     |  NO   | NO  |  NO    |   NO    |
[TheGamesDB]      |  <2>  | <2>  |  YES   |   YES  |   YES    |   YES   |    NO     |  NO   | NO  |  NO    | YouTube |
[GameFAQs]        |  <2>  | <2>  |  NO    |   NO   |   YES    |   YES   |    NO     |  NO   | NO  |  NO    |   NO    |
[MobyGames]       |  <2>  | <2>  |  NO    |   NO   |   YES    |   YES   |    YES    |  NO   | NO  |  NO    |   NO    |
[GiantBomb]       |  <3>  | <3>  |  <3>   |   <3>  |   YES    |   <3>   |    <3>    |  NO   | NO  |  NO    | YouTube |

  * `Banner` is a horizontal image with name of ROM/system. It is called `Wheel` in Hyperspin and `Logo` in HL.
     
     Also, HL has both `Logo`/`Wheel` and `Banner` in separated directories. I do not know the difference between them. 
     
     No idea about what is HL `Clearart`.

  * `Flyer` is a vertical image. It is called `Poster` in HL.

  * EmuMovies/HyperSpin Media provide 2D and 3D version of `Boxfront` and `Cartridges`.

  * <1> In the HyperSpin forum you can find per-game/per-system themes that have `Fanart` and `Banner`. However, in 
    many cases assets are inside SWF files and difficult to use outside HyperSpin.

  * <2> TheGamesDB/GameFAQs/MobyGames do not differentiate between `Title`/`Snap`. They just have screenshots.

  * GameFAQs have gamebox `Spine`, which can be considered a kind of `Banner`.

  * <3> GiantBomb has quite a lot of artwork. However, everything is mixed (`Title`, `Snaps`, `Fanart`, all showing
    on the same page) and makes it difficult to scrape. `Boxfront` is easy to scrape from GiantBomb.

  * RetroPie and Emulation Station users have nice No-Intro artwork collections including `Title`, `Snap` and `Boxfront`.

[EmuMovies]: http://emumovies.com/
[HyperSpin Media]: http://www.hyperspin-fe.com/files/category/2-hyperspin-media/
[No-Intro]: http://no-intro.dlgsoftware.net
[Retroarch]: https://github.com/libretro/libretro-thumbnails/
[TheGamesDB]: http://thegamesdb.net/
[GameFAQs]: http://www.gamefaqs.com/
[MobyGames]: http://www.mobygames.com/
[GiantBomb]: http://www.giantbomb.com/


## AEL artwork policy ##

 * One artwork directory will be required for every ROM launcher.
   User will be asked for one Artwork directory and AEL will create subdirectories inside 
   automatically.

 * To deal with Confluence (default) skin, user will be able to choose which artwork to 
   display as thumb/fanart. For example: thumb -> Boxfront, fanart -> Fanart.

 * No more separated thumb/fanart scrapers. Thumb/fanart scrapers will be unified into artwork 
   scrapers. Artwork scrapers will download all possible Artwork depending on site availabililty.

### ROM artwork storage ###

 1. Asset directory may be the same as the ROMs directory.

```
ROMs directory         ~/ROMs/SNES/Super Mario World (Europe).zip
Artwork directory      ~/Artwork/SNES/
Created automatically  ~/Artwork/SNES/titles/Super Mario World (Europe).png
                       ~/Artwork/SNES/snaps/Super Mario World (Europe).png
                       ~/Artwork/SNES/fanarts/Super Mario World (Europe).png
                       ~/Artwork/SNES/banners/Super Mario World (Europe).png
                       ~/Artwork/SNES/boxfronts/Super Mario World (Europe).png
                       ~/Artwork/SNES/boxbacks/Super Mario World (Europe).png
                       ~/Artwork/SNES/cartridges/Super Mario World (Europe).png
                       ~/Artwork/SNES/flyers/Super Mario World (Europe).png
                       ~/Artwork/SNES/maps/Super Mario World (Europe).png
                       ~/Artwork/SNES/manuals/Super Mario World (Europe).pdf
                       ~/Artwork/SNES/trailers/Super Mario World (Europe).mpeg
                       ~/Artwork/SNES/extrafanart/Super Mario World (Europe)/fanart1.png
                       ~/Artwork/SNES/extrafanart/Super Mario World (Europe)/fanart2.png
                       ~/Artwork/SNES/extrafanart/Super Mario World (Europe)/fanart3.png
```

### Launcher/Category artwork storage ###

 1. Category name `SEGA`. Each category will have a subdirectory with same name to store
    extrafanart.

 2. Launcher name `SNES (Retroarch bsnes balanced)`. Each launcher will have a subdirectory to
    store extrafanart.

```
Artwork directory  ADDON_DATA_DIR/asset-categories/
                   ADDON_DATA_DIR/asset-categories/SEGA/fanart1.png
                   ADDON_DATA_DIR/asset-categories/SEGA/fanart2.png
                   ADDON_DATA_DIR/asset-categories/SEGA/fanart3.png

Artwork directory  ADDON_DATA_DIR/asset-launchers/
                   ADDON_DATA_DIR/asset-launchers/SNES (Retroarch bsnes balanced)/fanart1.png
                   ADDON_DATA_DIR/asset-launchers/SNES (Retroarch bsnes balanced)/fanart2.png
                   ADDON_DATA_DIR/asset-launchers/SNES (Retroarch bsnes balanced)/fanart3.png
```

## Importing AL stuff into AEL ##

 * AL thumb will be imported as title.

 * AL fanart will be imported as fanart.

 * User will have to reorganise artwork directories to take full advantage of AEL
   capabilities after importing AL `launchers.xml`.






--------------------------------------------------------------------------------------------------------------




# TODO #

 * GameFAQs: detect when web server is blocked.
 
   Blocked IP Address
   Your IP address has been temporarily blocked due to a large number of HTTP requests. The most 
   common causes of this issue are:
 
   http://forum.kodi.tv/showthread.php?tid=287826&pid=2403674#pid2403674


# Multidisc support #

## ROM scanner implementation ##

 1) If the ROM scanner finds a multidisc image belonging to a set, for example
    `Final Fantasy VII (USA) (Disc 3).cue`.
 
    * The filename corresponds to the basename of the set.
 
    * The ROM basename is added to the `disks` list.

    * Asset names will have the basename of the set `Final Fantasy VII (USA)`.

```
    filename = '/home/kodi/ROMs/Final Fantasy VII (USA)'
    disks = ['Final Fantasy VII (USA) (Disc 3).cue']
```

 2) If the ROM scanner finds another image of the set then:
 
    * The basename is added to the `disks` list.
    
    * `disks` list is reordered so ROMs have consecutive order.
    
    * `filename` points to the first image of the set.
    
    * Metadata/Asset scraping is only done for the first ROM of the set.

```
    filename = '/home/kodi/ROMs/Final Fantasy VII (USA)'
    disks = ['Final Fantasy VII (USA) (Disc 1).cue', 'Final Fantasy VII (USA) (Disc 3).cue']
```

 3) ROMs not in a set have an empty `disks` list.

 4) This implementation is safe if there are missing ROMs in the set.
 
 5) Al launching time, users selects from a select dialog of the basenames of the roms of the
    set which one to launch.

## Naming conventions ##

[TOSEC Naming Convention]

[TOSEC Naming Convention]: http://www.tosecdev.org/tosec-naming-convention

 Organisation | Name example                                                |
--------------|-------------------------------------------------------------|
 TOSEC        | Final Fantasy VII (1999)(Square)(NTSC)(US)(Disc 1 of 2).cue |
              | Final Fantasy VII (1999)(Square)(NTSC)(US)(Disc 2 of 2).cue |
 Trurip       | Final Fantasy VII (EU) - (Disc 1 of 3).cue                  |
              | Final Fantasy VII (EU) - (Disc 2 of 3).cue                  |
              | Final Fantasy VII (EU) - (Disc 3 of 3).cue                  |
 Redump       | Final Fantasy VII (USA) (Disc 1).cue                        |
              | Final Fantasy VII (USA) (Disc 2).cue                        |
              | Final Fantasy VII (USA) (Disc 3).cue                        |


# TOSEC/Trurip/Redump image formats #

 TOSEC       | Redump  | Trurip          |
-------------|---------|-----------------|
 cue,iso,wav | cue,bin | cue,img,ccd,sub |


# AL subprocess module hack #


# listitem.setInfo() overlay values and effects #

`listitem.setInfo('video', {'overlay'  : 4})`

Kodi Krypton Estuary displays a small icon to the left of the listitem title that can be changed
with the overlay property value. Overlay values are defined in [GUIListItem],

```
enum GUIIconOverlay { ICON_OVERLAY_NONE = 0,
                      ICON_OVERLAY_RAR,
                      ICON_OVERLAY_ZIP,
                      ICON_OVERLAY_LOCKED,
                      ICON_OVERLAY_UNWATCHED,
                      ICON_OVERLAY_WATCHED,
                      ICON_OVERLAY_HD};
```

[setInfo]: http://mirrors.xbmc.org/docs/python-docs/16.x-jarvis/xbmcgui.html#ListItem-setInfo
[GUIListItem]: https://github.com/cisco-open-source/kodi/blob/master/xbmc/guilib/GUIListItem.h


# Development environment #

  1. Installed the packages `kodi` and `kodi-visualization-spectrum` in Debian.

  2. Kodi can be run from the command line in windowed mode.

  3. Created a basic package for AEL and install it from zip file.

  4. Once installed, addon code is located in `~/.kodi/addons/plugin.addon.name`

  5. Once installed, addon can be developed in place. A repository can be cloned in
     `~/.kodi/addons/plugin.addon.name`.


# Installing the addon from github #

It is very important that the addon files are inside the correct directory
`~/.kodi/addons/plugin.program.advanced.emulator.launcher`.

To install the plugin from Github, click on `Clone or download` -- `Download ZIP`.
This will download the repository contents to a ZIP file named
`plugin.program.advanced.emulator.launcher-master.zip`. Also, addon is
packed inside directory `plugin.program.advanced.emulator.launcher-master`.

This ZIP file should be decompressed, the directory renamed to
`plugin.program.advanced.emulator.launcher`, and packed into a ZIP file again.
Then, install the ZIP file.