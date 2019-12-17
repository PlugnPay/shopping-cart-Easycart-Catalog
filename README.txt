*** EasyCart Online Catalog ***
(For use with the EasyCart Shopping Cart)

README Revision: 07/24/08


Script Purpose:
---------------------
This script is used to dynamically generate an online catalog from the EasyCart shopping cart's product database.

* Important Note(s):
- You need to be sure your EasyCart shopping cart has been setup & works before you use this script.
- All products in your EasyCart product database must be assigned to a category. (See end of this file for details on how to set this.)


Script Support:
---------------------
This script & its related files are being provided "AS IS".  No technical support is implied or offered for this script.
This script, its features & all related integration issues stemming from said integration, will not be supported
 or addressed by our payment gateway or our respective partners.


This Script Requires:
---------------------
- A working EasyCart shopping cart setup
- Web Server running Perl v5.001 or newer
- Perl Modules:
  -- CGI          -> This should be have been pre-installed with any current version of Perl.
  -- LWP::Simple  -> This can be installed via your Perl package manager or download from "http://search.cpan.org"


How To Install:
---------------------
* Note: This document assumes you already have the EasyCart shopping cart setup, your web server runs Perl scripts and the above modules were installed.

1 - Open the 'easycart_catalog.cgi' file in a text editor (such as in Notepad)

2 - Edit the script's parameters between the "Script Parameters (Start Here)" & "Script Parameters (Stop Here)" lines.

3 - Save your changes the script, when completed.

4 - Upload the 'easycart_catalog.cgi' script into the CGI executable folder of your web site
    This folder is typically called 'cgi-bin' or 'cgi-local' on most servers.

5 - Set the file permissions of the 'easycart_catalog.cgi' file as '755' [read/write/execute for owner & read/execute for everyone else]

6 - Upload the rest of the files into the folder you specified in step #2

8 - Set the file permissions of the 3 template files as '644' [read/write for owner & read for everyone else]

9 - Set the file permissions of the 'orderfrm.prices' file as '666' [read/write for everyone]

10 - Open your browser & call the script's test mode.  This is done by typing in the script's URL into the address bar of your browser followed by "?test".
    For example: http://www.yoursite.com/cgi-bin/easycart_catalog.cgi?test

11 - Pay attention to the 'FILE ACCESS CHECK' section of that page.
    If everything worked correctly, it should look something like this:

    -----------------------------------

    FILE ACCESS CHECK:

    EasyCart Catalog Config:
    -- File OK
    EasyCart Catalog Database:
    -- File OK
    Main Template:
    -- File OK
    Category Template:
    -- File OK
    Category Template:
    -- File OK

    -----------------------------------

    If the script did not run, refer to the previous steps.
    If there are any read/write file errors, fix them accordingly.
    Do this until you fixed each issue noted & the test show OK for each entry.

12 - Open your browser and call the script's update mode.  This is done by typing in the script's URL into the address bar of your browser followed by "?update".
     For example: http://www.yoursite.com/cgi-bin/easycart_catalog.cgi?update

13 - You should see the contents of your EasyCart product database & a message telling you the script's database was updated.
     Re-run this script's update command any time you apply changes to your EasyCart product database, so the changes are reflected on your web site.

14 - To use the script, simply call the script via a button or hyperlink (with no special settings) from any of your web site's web pages.
     For example: http://www.yoursite.com/cgi-bin/easycart_catalog.cgi

     You're done...


Config File Parameters:
---------------------

This file contains all of the parameters for your EasyCart catalog script.
The format of the file can be either tab delimited or pipe ("|") delimited.
With one line per parameter, with the 1st being the name and the 2nd being the value of that parameter.

For Example, if your merchant username was 'pnpdemo', you would enter:

  If using pipes:   merchant|pnpdemo

    or

  If using tabs:    merchant[tab]pnpdemo
  (where [tab] in the above example is where the hard tab would be placed)


The allowed parameters for the config.txt file are as follows:

'payment_gateway_domain'
  # This is the domain name to your EasyCart shopping cart; change if necessary.
  Default: easycart.plugnpay.com

'merchant'
  # Your gateway login username
  Default: put-username-here (replace with your username)

'main_link_format'
  # Format of the category navigation menu
    Valid options are:
     -- 'form' (shows HTML Form Buttons)
     -- 'link' (shows Text Hyperlinks)
  Default: link

'orderform_type'
  # Shows multi-products or a single product order forms.
    Valid options are:
    -- 'multi'  (main menu provided a order form with all products which belong to that category)
    -- 'single' (main menu provides a list of all products which belong to that category.  User selects product to get to a single product order form)
  Default: single

'format'
  # Format of the order forms.
    Valid options are:
    -- 'no_border_table' (Table Without Visible Borders)
    -- 'border_table'    (Table With Visible Borders)
    -- 'plain_text'      (Plain Text Format)
  Default: no_border_table

'show_long_description'
  # Show the product long description ['yes' or 'no']
  Default: no

'show_shipping'
  # Show the product shipping fee ['yes' or 'no']
  Default: no

'show_weight'
  # Show the product weight ['yes' or 'no']
  Default: no

'show_graphic'
  # Show the product graphic ['yes' or 'no']
  Default: no

'image_folder'
  # URL to the image folder for use with your order forms graphics [no "/" at end of URL]
  Default: http://www.your-domain-name.com/your-image-folder (replace with your site's URL)

'checkstock'
  # Activate checkstock flag in order forms. ['yes' or 'no']
    Valid options are:
    -- 'yes' (will include the 'checkstock' flag within the EasyCart order forms.)
    -- 'no'  (set to 'no' to allow out of stock orders.)
  Default: no

'allow_outofstock_orders'
  # Allows orders to be taken for out of stock products [when instock is 'no' in database] ['yes' or 'no']
    Valid options are:
    -- 'yes' (will show message about product being back ordered & will allow the item to be ordered.)
    -- 'no'  (hides the quantity box for this product & will allow out of stock orders to be placed.)
    * Note: the 'checkstock' setting will supersede the 'allow_outofstock_orders' setting...
  Default: no

'match_site'
  # Matches 'site' column in EasyCart product database, so only those matching products show.
    Leave blank to show all products.
  Default: (left blank)

'continue'
  # Set this to an exact URL where you want the EasyCart's Continue buttons to redirect to.
    Leave blank to return back to this script's main menu.
    If in doubt, leave alone & it will return back to this script's main menu.
  Default: (left blank)

'digital_download_extensions'
  # List digital download file extensions here, separate by a pipe (“|”) character.
    Leave this alone if not using Digital Download]
  Default: htm|html|txt|pdf|zip

'category_count'
  # Shows number of products available in each category in vertical category menu ['yes' or 'no']
  Default: yes

'ec_version'
  # Indicates which Smart Screens payment script EasyCart calls at time of checkout.
    Valid options are:
    -- '1.0' (tells EasyCart to use the merchant's old payment script at time of checkout [i.e. USERNAMEpay.cgi])
    -- '2.0' (tells EasyCart to use the standard shared payment script at time of checkout [i.e. pay.cgi])
    * Note: The '1.0' option only applies to accounts setup before 08/23/04.
            For everyone else, leave it set to '2.0' for correct usage with your account.   
  Default: 2.0


Usage Notes:
---------------------

- Special EasyCart product database columns have been created just for this script.  Such as for product description attributes & an web site assignment fields for use with EasyCart being shared with multiple web sites.
  See the "EasyCart Product Database Specifications" document in your account's documentation section for details

  *** IMPORTANT ***
  The 'Category' field is required in your EasyCart product database for each product you enter when using this script.
  *****************


- To test the script to see if it was setup correctly, call the script's test mode.  This is done by typing in the script's URL into the address bar of your browser followed by "?test".
    For example: http://www.yoursite.com/cgi-bin/easycart_catalog.cgi?test

- To update the script's database, call the script's update mode.  This is done by typing in the script's URL into the address bar of your browser followed by "?update".
    For example: http://www.yoursite.com/cgi-bin/easycart_catalog.cgi?update

- The 3 templates web pages can be modified to fit the look and feel of your web site.

  The following tags can be added to the templates, to designate where things will be placed.

  --> Place [table] in the web page where you want the product data or listing to be placed.
  --> Place [search] in the web page where you want a search option to be placed.
  --> Place [checkout] in the web page where you want a shopping cart checkout button to be placed.
  --> Place [menu_row] in the web page where you want a horizontal listing of the product category menu to be placed.
  --> Place [menu_column] in the web page where you want a vertical listing of the product category menu to be placed.

  (* Note: only [table] is required to be in the templates.  All the other tags are optional and not required to be in the template.) 

- The 'template_main.htm' web page is the template used for the script's main category menu
- The 'template_category.htm' web page is the template used when the script lists all the products within a given category
- The 'template_orderform.htm' web page is the template used for the actual EasyCart order form, where the customer selects the quantity of the product



Required EasyCart Product Database Column:
---------------------
Below is the description of the required EasyCart Product Database 'Category' column.
It is used to define the category the product falls within.
This MUST be in your EasyCart product database in order to use this script.

You can add this column manually to your EasyCart product database using the Edit feature under the Advanced menu in your EasyCart Administration Area or easily via the Product Database Wizard.

This parameter is added to the 'header' line in the EasyCart Product Database.

The default (required) header line format looks like this:
header "ProductID","UnitPrice","Shipping","Description"

To add a new database column simply place a ',' (comma) followed by the new column name
(enclosed within double quotes) at the end of the 'header' line.

For Example:
header "ProductID","UnitPrice","Shipping","Description","Category"

* NOTE: The Category column name is case sensitive and MUST be entered in exact the case you see it in this document.


An example product would be as such:
"def","199.00","3.00","White Pearl Earrings 7-1/2mm w/2 dia., 1/4 crt, 14 kt","Earrings"

This would assign the product the the 'Earrings' category.  Simply create whatever names you want for each category for each product.
Valid characters for the 'Category' column are letters, numbers, spaces & hyphens.
This is case sensitive, so type in the value as you want it to appear in your EasyCart online catalog.

Additional columns are also available.  Please see the 'EasyCart Product Database Specifications' document in your EasyCart Administration Area for details.

