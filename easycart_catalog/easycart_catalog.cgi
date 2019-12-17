#!/usr/bin/perl

#################################################
#  EasyCart Online Catalog
#  - For Use with the EasyCart Shopping Cart
#  - Last Updated 08/17/10
#################################################

require 5.001;
$| = 1;

use CGI;
use LWP::Simple;
#use strict;

my $query = new CGI;

my @array = $query->param;
foreach $var (@array) {
  $query{$var} = $query->param($var);
}


#####################################################
# Script Parameters (Start Here)
#####################################################

# set self-location of this script -> should never need to be changed...
my $script = "http://" . $ENV{'HTTP_HOST'} . $ENV{'SCRIPT_NAME'};

# set relative or absolute path to the folder where the config, template and database files are stored [No Trailing Slash Allowed]
my $data_folder = "/var/www/cgi-bin";

#####################################################
# Script Parameters (Stop Here)
#####################################################


print "Content-type: text/html\n\n";

# set default parameters for config fields here
my %config = {
  "allow_outofstock_orders", "no",
  "category_count", "yes",
  "checkstock", "no",
  "continue", "$script",
  "digital_download_extensions", "htm|html|txt|pdf|zip",
  "format", "no_border_table",
  "image_folder", "http://www.your-domain-name.com/your-image-folder",
  "main_link_format", "link",
  "match_site", "",
  "merchant", "put-username-here",
  "orderform_type", "single",
  "payment_gateway_domain", "easycart.plugnpay.com",
  "show_graphic", "no",
  "show_long_description", "no",
  "show_shipping", "no",
  "show_weight", "no",
  "ec_version", "2.0"
};

# read configuration file into memory & update as necessary
open (CONFIG, "$data_folder/config.txt") or print "Cannot open $data_folder/config.txt for reading. $!";
while (<CONFIG>) {
  my $theline = $_;
  if (($theline =~ /\w/) && ($theline =~ /\t|\|/)) {
    my @temp;

    if ($theline =~ /\|/) { 
      @temp = split(/\|/, $theline, 2);
    }
    else {
      @temp = split(/\t/, $theline, 2);
    }

    if ($temp[0] =~ /^([a-zA-Z])/) {
      $temp[1] =~ s/(\r|\n|\r\n|\n\r)//g; # remove new lines & carriage returns
      $config{$temp[0]} = $temp[1];
    }
  }
}
close (CONFIG);

# check for merchant username
if ($config{'merchant'} =~ /put-username-here/i) {
  print "<b>ERROR: Missing merchant username in \'$data_folder/config.txt\' file.</b>\n";
  print "<br>Please ensure you configured the $data_folder/congfig.txt file correctly.\n";
  exit;
}

# figure out what mode/function to call
if ($ENV{'QUERY_STRING'} eq "update") {
  &download_update();
}
elsif ($ENV{'QUERY_STRING'} eq "test") {
  &run_test();
}
elsif ($query{'mode'} eq "show_category") {
  if (($config{'orderform_type'} eq "single") && ($query{'sku'} ne "")) {
    &show_category_single();
  }
  elsif ($config{'orderform_type'} eq "single") {
    &show_category_list();
  }
  else {
    &show_category_all();
  }
}
elsif ($query{'mode'} eq "search") {
  &search();
}
else {
  &main_page();
}

exit;

sub main_page {
  my $page_data;
  my %category_hash;

  open(INFILE, "$data_folder/orderfrm.prices") or print "Can't open $data_folder/orderfrm.prices for reading. $!\n";
  while(<INFILE>) {
    chop;
    my $theline = $_;

    if ($theline =~ m/\t/) {
      $theline =~ s/\"//g;
      @array = split(/\t/, $theline);
    }
    else {
      @array = split(/\"\,\"/, $theline);
      $array[0] =~ s/\"//g;
      $array[$#array] =~ s/\"//g;
    }

    if ($array[0] =~ /header /) {
      for (my $aaa = 0; $aaa <= $#array; $aaa++) {
        print "<!-- $array[$aaa] == $aaa -->\n";
        &assign_columns("$array[$aaa]", "$aaa");
      }
    }

    # produce hash of category names here
    if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
      my $category_name = $array[$category_column];
      $category_name =~ s/ /\_/g;
      $category_name =~ s/\W//g; # remove non-allowed characters
      #$category_name =~ s/(\r|\n|\r\n|\n\r)//g; # remove new lines & carriage returns
      if ($category_name eq "") {
        $category_name = "Uncategorized";
      }
      $category_hash{"$category_name"} = $category_hash{"$category_name"} + 1;
    }
  }
  close(INFILE);

  $page_data .= "<div align=\"center\">\n";

  if ($config{'format'} eq "border_table") {
    $page_data .= "<table border=\"1\">\n";
  }
  else {
    $page_data .= "<table border=\"0\">\n";
  }
  $page_data .= "  <tr>\n";
  $page_data .= "    <th>Please Select A Product Category:</th>\n";
  $page_data .= "  </tr>\n";

  foreach $key (sort keys %category_hash) {
    my $category_name = $key;
    $category_name =~ s/\_/ /g;

    $page_data .= "  <tr>\n";

    if ($config{'main_link_format'} eq "link") {
      $page_data .= "    <td align=\"center\"><a href=\"$script\?mode=show_category&category=$category_name\">";
      if ($category_name ne "") {
        $page_data .= "$category_name - ";
      }
      $page_data .= "$category_hash{\"$key\"} Products</a></td>\n";
    }
    else { # where $config{'main_link_format'} eq "form" or undefined
      $page_data .= "<form method=\"post\" action=\"$script\">\n";
      $page_data .= "<input type=\"hidden\" name=\"mode\" value=\"show_category\">\n";
      $page_data .= "<input type=\"hidden\" name=\"category\" value=\"$category_name\">\n";
      if ($category_name eq "") {
        $page_data .= "    <td align=\"center\"><input type=\"submit\" value=\"$category_hash{\"$key\"} Products\"></td>\n";
      }
      else {
        $page_data .= "    <td align=\"center\"><input type=\"submit\" value=\"$category_name - $category_hash{\"$key\"} Products\"></td>\n";
      }
      $page_data .= "</form>\n";
    }

    $page_data .= "  </tr>\n";
  }

  $page_data .= "</table>\n";

  $page_data .= "<p><form method=\"post\" action=\"http://$config{'payment_gateway_domain'}/easycart.cgi\">\n";
  $page_data .= "<input type=\"hidden\" name=\"username\" value=\"$config{'merchant'}\">\n";
  $page_data .= "<input type=\"hidden\" name=\"function\" value=\"checkout\">\n";
  $page_data .= "<input type=\"hidden\" name=\"ec_version\" value=\"$config{'ec_version'}\">\n";
  if ($config{'continue'} ne "") {
    $page_data .= "<input type=\"hidden\" name=\"continue\" value=\"$config{'continue'}\">\n";
  }
  $page_data .= "<input type=\"submit\" value=\"View Shopping Cart\">\n";
  $page_data .= "</form>\n";

  $page_data .= "</div>\n";

  # make necessary forms
  my $search_form = &create_search_form();
  my $checkout_form .= &create_checkout_form();
  my $menu_row_form = &create_menu_row_form(%category_hash);
  my $menu_column_form = &create_menu_column_form(%category_hash);

  # send page to screen
  open(TEMPLATE, "$data_folder/template_main.htm") or print "Cannot open $data_folder/template_main.htm for reading. $!\n";
  while(<TEMPLATE>) {
    my $theline = $_;

    if ($theline =~ /\[table\]/) {
      $theline =~ s/\[table\]/$page_data/g;
    }

    if ($theline =~ /\[search\]/) {
      $theline =~ s/\[search\]/$search_form/g;
    }

    if ($theline =~ /\[checkout\]/) {
      $theline =~ s/\[checkout\]/$checkout_form/g;
    }

    if ($theline =~ /\[menu_row\]/) {
      $theline =~ s/\[menu_row\]/$menu_row_form/g;
    }

    if ($theline =~ /\[menu_column\]/) {
      $theline =~ s/\[menu_column\]/$menu_column_form/g;
    }

    print $theline;
  }
  close(TEMPLATE);

  return;
}

sub show_category_list {
  my $page_data;
  my %category_hash;

  $page_data .= "<div align=\"center\">\n";

  if ($config{'format'} == "border_table") {
    $page_data .= "<table border=\"0\">\n";
  }
  else {
    $page_data .= "<table border=\"0\">\n";
  }
  $page_data .= "  <tr>\n";
  $page_data .= "    <th colspan=\"3\">Please Select A Product:</th>\n";
  $page_data .= "  </tr>\n";

  open(DATABASE, "$data_folder/orderfrm.prices") or print "Can't open $data_folder/orderfrm.prices for reading. $!";
  while(<DATABASE>) {
    chop;
    $theline = $_;

    if ($theline =~ m/\t/) {
      $theline =~ s/\"//g;
      @array = split(/\t/, $theline);
    }
    else {
      @array = split(/\"\,\"/, $theline);
      $array[0] =~ s/\"//g;
      $array[$#array] =~ s/\"//g;
    }

    if ($array[0] =~ /header /) {
      for (my $aaa = 0; $aaa <= $#array; $aaa++) {
        &assign_columns("$array[$aaa]", "$aaa");
      }
    }

    # produce hash of category names here
    if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
      my $category_name = $array[$category_column];
      $category_name =~ s/ /\_/g;
      $category_name =~ s/\W//g; # remove non-allowed characters
      #$category_name =~ s/(\r|\n|\r\n|\n\r)//g; # remove new lines & carriage returns
      if ($category_name eq "") {
        $category_name = "Uncategorized";
      }
      $category_hash{"$category_name"} = $category_hash{"$category_name"} + 1;
    }

    if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && ($array[$category_column] =~ /^$query{'category'}/i) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
      $page_data .= "  <tr>\n";
      if ($config{'main_link_format'} eq "link") {
        $page_data .= "    <td align=\"center\"><a href=\"$script\?mode=show_category\&category=$array[$category_column]\&sku=$array[0]\">$array[3] - \$$array[1]</a></td>\n";
      }
      else { # where $config{'main_link_format'} eq "form" or undefined
        $page_data .= "    <td align=\"center\">$array[3]"; # item description
        $page_data .= "    <td align=\"center\">\$$array[1]"; # item price
        $page_data .= "<form method=\"post\" action=\"$script\">\n";
        $page_data .= "<input type=\"hidden\" name=\"mode\" value=\"show_category\">\n";
        $page_data .= "<input type=\"hidden\" name=\"category\" value=\"$array[$category_column]\">\n";
        $page_data .= "<input type=\"hidden\" name=\"sku\" value=\"$array[0]\">\n";
        $page_data .= "    <td align=\"center\">&nbsp; <input type=\"submit\" value=\"More Info\"></td>\n";
        $page_data .= "</form>\n";
      }
      $page_data .= "  </tr>\n";
    }
  }
  close(DATABASE);

  $page_data .= "</table>\n";

  $page_data .= "<p><form method=\"post\" action=\"$script\">\n";
  $page_data .= "<input type=\"submit\" value=\"Catalog Main Menu\">\n";
  $page_data .= "</form>\n";

  $page_data .= "<form method=\"post\" action=\"http://$config{'payment_gateway_domain'}/easycart.cgi\">\n";
  $page_data .= "<input type=\"hidden\" name=\"username\" value=\"$config{'merchant'}\">\n";
  $page_data .= "<input type=\"hidden\" name=\"function\" value=\"checkout\">\n";
  $page_data .= "<input type=\"hidden\" name=\"ec_version\" value=\"$config{'ec_version'}\">\n";
  if ($config{'continue'} ne "") {
    $page_data .= "<input type=\"hidden\" name=\"continue\" value=\"$config{'continue'}\">\n";
  }
  $page_data .= "<input type=\"submit\" value=\"View Shopping Cart\">\n";
  $page_data .= "</form>\n";

  $page_data .=  "</div>\n";


  # make necessary forms
  my $search_form = &create_search_form();
  my $checkout_form .= &create_checkout_form();
  my $menu_row_form = &create_menu_row_form(%category_hash);
  my $menu_column_form = &create_menu_column_form(%category_hash);

  # send page to screen
  open(TEMPLATE, "$data_folder/template_category.htm") or print "Cannot open $data_folder/template_category.htm for reading. $!\n";
  while(<TEMPLATE>) {
    $theline = $_;

    if ($theline =~ /\[table\]/) {
      $theline =~ s/\[table\]/$page_data/g;
    }

    if ($theline =~ /\[search\]/) {
      $theline =~ s/\[search\]/$search_form/g;
    }

    if ($theline =~ /\[checkout\]/) {
      $theline =~ s/\[checkout\]/$checkout_form/g;
    }

    if ($theline =~ /\[menu_row\]/) {
      $theline =~ s/\[menu_row\]/$menu_row_form/g;
    }

    if ($theline =~ /\[menu_column\]/) {
      $theline =~ s/\[menu_column\]/$menu_column_form/g;
    }

    print $theline;
  }
  close(TEMPLATE);

  return;
}

sub show_category_all {
  my $page_data;
  my %category_hash;

  if ($config{'format'} eq "no_border_table") {
    $query{'view_border'} = "0";  # table with no borders
  }
  elsif ($config{'format'} eq "border_table") {
    $query{'view_border'} = "1";  # table with borders
  }
  elsif ($config{'format'} eq "plain_text") {
    $query{'view_border'} = "1";  # plan text - no tables
  }

  $page_data .= "<div align=\"center\">\n";

  $page_data .= "<form name=\"ezcart\" action=\"http://$config{'payment_gateway_domain'}/easycart.cgi\" method=\"post\">\n";
  $page_data .= "<input type=\"hidden\" name=\"username\" value=\"$config{'merchant'}\">\n";
  $page_data .= "<input type=\"hidden\" name=\"function\" value=\"add\">\n";
  $page_data .= "<input type=\"hidden\" name=\"ec_version\" value=\"$config{'ec_version'}\">\n";

  if ($config{'checkstock'} eq "yes") {
    $page_data .= "<input type=\"hidden\" name=\"checkstock\" value=\"yes\">\n";
  }

  if ($config{'continue'} ne "") {
    $page_data .= "<input type=\"hidden\" name=\"continue\" value=\"$config{'continue'}\">\n";
  }

  ### For table form format
  if (($config{'format'} eq "no_border_table") || ($config{'format'} eq "border_table")) {
    $page_data .= "<table border=\"$query{'view_border'}\" width=\"75\%\">\n";
    $page_data .= "  <tr>\n";
    if ($config{'show_graphic'} eq "yes") {
      $page_data .= "    <th>&nbsp;</th>\n";
    }
    $page_data .= "    <th>Product Description</th>\n";
    $page_data .= "    <th>Price</th>\n";
    if ($config{'show_shipping'} ne "no") {
      $page_data .= "    <th>Shipping</th>\n";
    }
    $page_data .= "    <th>Quantity</th>\n";
    $page_data .= "  </tr>\n";

    open(DATABASE, "$data_folder/orderfrm.prices") or print "Can't open $data_folder/orderfrm.prices for reading. $!";
    while(<DATABASE>) {
      chop;
      $theline = $_;

      if ($theline =~ m/\t/) {
        $theline =~ s/\"//g;
        @array = split(/\t/, $theline);
      }
      else {
        @array = split(/\"\,\"/, $theline);
        $array[0] =~ s/\"//g;
        $array[$#array] =~ s/\"//g;
      }

      if ($array[0] =~ /header /) {
        for (my $aaa = 0; $aaa <= $#array; $aaa++) {
          &assign_columns("$array[$aaa]", "$aaa");
        }
      }

      # produce hash of category names here
      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        my $category_name = $array[$category_column];
        $category_name =~ s/ /\_/g;
        $category_name =~ s/\W//g; # remove non-allowed characters
        #$category_name =~ s/(\r|\n|\r\n|\n\r)//g; # remove new lines & carriage returns
        if ($category_name eq "") {
          $category_name = "Uncategorized";
        }
        $category_hash{"$category_name"} = $category_hash{"$category_name"} + 1;
      }

      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && ($array[$category_column] =~ /^$query{'category'}/i) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        $i++;
        $page_data .= "  <tr>\n";
        if (($config{'show_graphic'} eq "yes") && ($array[$graphic_column] eq "")) {
          $page_data .= "  <td align=\"center\">Sorry, no image is available.</td>\n";
        }
        elsif ($config{'show_graphic'} eq "yes") {
          $page_data .= "  <td align=\"center\"><img src=\"$config{'image_folder'}/$array[$graphic_column]\"></td>\n";
        }
        $page_data .= "    <td align=\"center\"><input type=\"hidden\" name=\"item$i\" value=\"$array[0]\">$array[3]"; # item SKU & description

        # display product's long description
        if (($config{'show_long_description'} eq "yes") && ($array[$long_description_column] ne "") && ($long_description_column ne "")) {
          $page_data .= "<br>$array[$long_description_column]\n";
        }

        # display product's weight
        if (($config{'show_weight'} eq "yes") && ($array[$weight_column] ne "") && ($weight_column ne "")) {
          $page_data .= "<br>Weight: $array[$weight_column] Lbs.\n";
        }

        # display product attribute options
        if (($array[$descra_column] =~ /\w/) && ($descra_column ne "")) {
          my @descra_temp = split(/\:/, $array[$descra_column], 2);
          my @descra_temp2 = split(/\|/, $descra_temp[1]);
          $page_data .= "<br>$descra_temp[0]\: <select name=\"descra$i\">\n";
          for (my $a = 0; $a <= $#descra_temp2; $a++) {
            $page_data .= "<option value=\"$descra_temp2[$a]\">$descra_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrb_column] =~ /\w/) && ($descrb_column ne "")) {
          my @descrb_temp = split(/\:/, $array[$descrb_column], 2);
          my @descrb_temp2 = split(/\|/, $descrb_temp[1]);
          $page_data .= "<br>$descrb_temp[0]\: <select name=\"descrb$i\">\n";
          for (my $a = 0; $a <= $#descrb_temp2; $a++) {
            $page_data .= "<option value=\"$descrb_temp2[$a]\">$descrb_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrc_column] =~ /\w/) && ($descrc_column ne "")) {
          my @descrc_temp = split(/\:/, $array[$descrc_column], 2);
          my @descrc_temp2 = split(/\|/, $descrc_temp[1]);
          $page_data .= "<br>$descrc_temp[0]\: <select name=\"descrc$i\">\n";
          for (my $a = 0; $a <= $#descrc_temp2; $a++) {
            $page_data .= "<option value=\"$descrc_temp2[$a]\">$descrc_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }

        $page_data .= "</td>\n";
        $page_data .= "    <td align=\"center\">\$$array[1]</td>\n";
        if ($config{'show_shipping'} ne "no") {
          $page_data .= "    <td align=\"center\">\$$array[2]</td>\n";
        }

        $page_data .= "    <td align=\"center\">";
        if (($array[$instock_column] =~ /n/i) && ($instock_column ne "") && ($config{'allow_outofstock_orders'} eq "yes") && ($config{'checkstock'} ne "yes")) {
          $page_data .= "<i>This item is<br>back ordered.</i>\n";
          $page_data .= "<br><input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
        }
        elsif (($array[$instock_column] =~ /n/i) && ($instock_column ne "")) {
          $page_data .= "Sorry, this item<br>is not in stock.\n";
        }
        else {
          if ($array[0] =~ /\.($config{'digital_download_extensions'})$/i) {
            $page_data .= "<input type=\"checkbox\" name=\"quantity$i\" value=\"1\"> Check To Add\n";
          }
          else {
            $page_data .= "<input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
          }
        }
        $page_data .= "</td>\n";

        $page_data .= "  </tr>\n";
      }
    }
    close(DATABASE);

    $page_data .= "</table>\n";
  }  # End tabled form format

  ### begin plain text format
  if ($config{'format'} eq "plain_text") {
    open(DATABASE, "$data_folder/orderfrm.prices") or print "Can't open $data_folder/orderfrm.prices for reading. $!";
    while(<DATABASE>) {
      chop;
      $theline = $_;

      if ($theline =~ m/\t/) {
        $theline =~ s/\"//g;
        @array = split(/\t/, $theline);
      }
      else {
        @array = split(/\"\,\"/, $theline);
        $array[0] =~ s/\"//g;
        $array[$#array] =~ s/\"//g;
      }

      if ($array[0] =~ /header /) {
        for (my $aaa = 0; $aaa <= $#array; $aaa++) {
          &assign_columns("$array[$aaa]", "$aaa");
        }
      }

      # produce hash of category names here
      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        my $category_name = $array[$category_column];
        $category_name =~ s/ /\_/g;
        $category_name =~ s/\W//g; # remove non-allowed characters
        #$category_name =~ s/(\r|\n|\r\n|\n\r)//g; # remove new lines & carriage returns
        if ($category_name eq "") {
         $category_name = "Uncategorized";
        }
        $category_hash{"$category_name"} = $category_hash{"$category_name"} + 1;
      }

      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && ($array[$category_column] =~ /^$query{'category'}/i) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        $i++;
        $page_data .= "<p>\n";
        if (($config{'show_graphic'} eq "yes") && ($array[$graphic_column] eq "")) {
          $page_data .= "<br>Sorry, no image is available.\n";
        }
        elsif ($config{'show_graphic'} eq "yes") {
          $page_data .= "<br><img src=\"$config{'image_folder'}/$array[$graphic_column]\">\n";
        }
        $page_data .= "<input type=\"hidden\" name=\"item$i\" value=\"$array[0]\">\n"; # item SKU
        $page_data .= "<br><b>$array[3]</b>\n"; # description

        # display product's long description
        if (($config{'show_long_description'} eq "yes") && ($array[$long_description_column] ne "") && ($long_description_column ne "")) {
          $page_data .= "<br>$array[$long_description_column]\n";
        }

        # display product's weight
        if (($config{'show_weight'} eq "yes") && ($array[$weight_column] ne "") && ($weight_column ne "")) {
          $page_data .= "<br>Weight: $array[$weight_column] Lbs.\n";
        }

        # display product attribute options
        if (($array[$descra_column] =~ /\w/) && ($descra_column ne "")) {
          my @descra_temp = split(/\:/, $array[$descra_column], 2);
          my @descra_temp2 = split(/\|/, $descra_temp[1]);
          $page_data .= "<br>$descra_temp[0]\: <select name=\"descra$i\">\n";
          for (my $a = 0; $a <= $#descra_temp2; $a++) {
            $page_data .= "<option value=\"$descra_temp2[$a]\">$descra_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrb_column] =~ /\w/) && ($descrb_column ne "")) {
          my @descrb_temp = split(/\:/, $array[$descrb_column], 2);
          my @descrb_temp2 = split(/\|/, $descrb_temp[1]);
          $page_data .= "<br>$descrb_temp[0]\: <select name=\"descrb$i\">\n";
          for (my $a = 0; $a <= $#descrb_temp2; $a++) {
            $page_data .= "<option value=\"$descrb_temp2[$a]\">$descrb_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrc_column] =~ /\w/) && ($descrc_column ne "")) {
          my @descrc_temp = split(/\:/, $array[$descrc_column], 2);
          my @descrc_temp2 = split(/\|/, $descrc_temp[1]);
          $page_data .= "<br>$descrc_temp[0]\: <select name=\"descrc$i\">\n";
          for (my $a = 0; $a <= $#descrc_temp2; $a++) {
            $page_data .= "<option value=\"$descrc_temp2[$a]\">$descrc_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }

        $page_data .= "<br>Price: \$$array[1]\n";
        if ($config{'show_shipping'} ne "no") {
          $page_data .= "<br>Shipping: \$$array[2]\n";
        }

        if (($array[$instock_column] =~ /n/i) && ($instock_column ne "") && ($config{'allow_outofstock_orders'} eq "yes") && ($config{'checkstock'} ne "yes")) {
          $page_data .= "<br><i>This item is back ordered.</i>\n";
          $page_data .= "<br>Quantity: <input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
        }
        elsif (($array[$instock_column] =~ /n/i) && ($instock_column ne "")) {
          $page_data .= "<br>Sorry, this item is not in stock.\n";
        }
        else {
          if ($array[0] =~ /.($config{'digital_download_extensions'})$/i) {
            $page_data .= "<input type=\"checkbox\" name=\"quantity$i\" value=\"1\"> Check To Add\n";
          }
          else {
            $page_data .= "<input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
          }
        }
      }
    }
  }  # End plain text format

  $page_data .= "<p><input type=\"submit\" value=\"Add To Cart\" name=\"order\"> \&nbsp; <input type=\"reset\" value\=\"Reset Form\">\n";
  $page_data .= "</form>\n";

  $page_data .= "<p><form method=\"post\" action=\"$script\">\n";
  $page_data .= "<input type=\"submit\" value=\"Catalog Main Menu\">\n";
  $page_data .= "</form>\n";

  $page_data .= "<form method=\"post\" action=\"http://$config{'payment_gateway_domain'}/easycart.cgi\">\n";
  $page_data .= "<input type=\"hidden\" name=\"username\" value=\"$config{'merchant'}\">\n";
  $page_data .= "<input type=\"hidden\" name=\"function\" value=\"checkout\">\n";
  $page_data .= "<input type=\"hidden\" name=\"ec_version\" value=\"$config{'ec_version'}\">\n";
  if ($config{'continue'} ne "") {
    $page_data .= "<input type=\"hidden\" name=\"continue\" value=\"$config{'continue'}\">\n";
  }
  $page_data .= "<input type=\"submit\" value=\"View Shopping Cart\">\n";
  $page_data .= "</form>\n";

  $page_data .= "</div>\n";

  # make necessary forms
  my $search_form = &create_search_form();
  my $checkout_form .= &create_checkout_form();
  my $menu_row_form = &create_menu_row_form(%category_hash);
  my $menu_column_form = &create_menu_column_form(%category_hash);

  # send page to screen
  open(TEMPLATE, "$data_folder/template_orderform.htm") or print "Cannot open $data_folder/template_orderform.htm for reading. $!\n";
  while(<TEMPLATE>) {
    $theline = $_;

    if ($theline =~ /\[table\]/) {
      $theline =~ s/\[table\]/$page_data/g;
    }

    if ($theline =~ /\[search\]/) {
      $theline =~ s/\[search\]/$search_form/g;
    }

    if ($theline =~ /\[checkout\]/) {
      $theline =~ s/\[checkout\]/$checkout_form/g;
    }

    if ($theline =~ /\[menu_row\]/) {
      $theline =~ s/\[menu_row\]/$menu_row_form/g;
    }

    if ($theline =~ /\[menu_column\]/) {
      $theline =~ s/\[menu_column\]/$menu_column_form/g;
    }

    print $theline;
  }
  close(TEMPLATE);

  return;
}

sub show_category_single {
  my $page_data;
  my %category_hash;

  if ($config{'format'} eq "no_border_table") {
    $query{'view_border'} = "0";  # table with no borders
  }
  elsif ($config{'format'} eq "border_table") {
    $query{'view_border'} = "1";  # table with borders
  }
  elsif ($config{'format'} eq "plain_text") {
    $query{'view_border'} = "1";  # plan text - no tables
  }

  $page_data .= "<div align=\"center\">\n";

  $page_data .= "<form name=\"ezcart\" action=\"http://$config{'payment_gateway_domain'}/easycart.cgi\" method=\"post\">\n";
  $page_data .= "<input type=\"hidden\" name=\"username\" value=\"$config{'merchant'}\">\n";
  $page_data .= "<input type=\"hidden\" name=\"function\" value=\"add\">\n";
  $page_data .= "<input type=\"hidden\" name=\"ec_version\" value=\"$config{'ec_version'}\">\n";

  if ($config{'checkstock'} eq "yes") {
    $page_data .= "<input type=\"hidden\" name=\"checkstock\" value=\"yes\">\n";
  }

  if ($config{'continue'} ne "") {
    $page_data .= "<input type=\"hidden\" name=\"continue\" value=\"$config{'continue'}\">\n";
  }

  ### For table form format
  if (($config{'format'} eq "no_border_table") || ($config{'format'} eq "border_table")) {
    $page_data .= "<table border=\"$query{'view_border'}\" width=\"75\%\">\n";
    $page_data .= "  <tr>\n";
    if ($config{'show_graphic'} eq "yes") {
      $page_data .= "    <th>&nbsp;</th>\n";
    }
    $page_data .= "    <th>Product Description</th>\n";
    $page_data .= "    <th>Price</th>\n";
    if ($config{'show_shipping'} ne "no") {
      $page_data .= "    <th>Shipping</th>\n";
    }
    $page_data .= "    <th>Quantity</th>\n";
    $page_data .= "  </tr>\n";

    open(DATABASE, "$data_folder/orderfrm.prices") or print "Can't open $data_folder/orderfrm.prices for reading. $!";
    while(<DATABASE>) {
      chop;
      $theline = $_;

      if ($theline =~ m/\t/) {
        $theline =~ s/\"//g;
        @array = split(/\t/, $theline);
      }
      else {
        @array = split(/\"\,\"/, $theline);
        $array[0] =~ s/\"//g;
        $array[$#array] =~ s/\"//g;
      }

      if ($array[0] =~ /header /) {
        for (my $aaa = 0; $aaa <= $#array; $aaa++) {
          &assign_columns("$array[$aaa]", "$aaa");
        }
      }

      # produce hash of category names here
      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        my $category_name = $array[$category_column];
        $category_name =~ s/ /\_/g;
        $category_name =~ s/\W//g; # remove non-allowed characters
        #$category_name =~ s/(\r|\n|\r\n|\n\r)//g; # remove new lines & carriage returns
        if ($category_name eq "") {
          $category_name = "Uncategorized";
        }
        $category_hash{"$category_name"} = $category_hash{"$category_name"} + 1;
      }

      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && ($array[$category_column] =~ /^$query{'category'}/i) && ($array[0] eq "$query{'sku'}") && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        $i++;
        $page_data .= "  <tr>\n";
        if (($config{'show_graphic'} eq "yes") && ($array[$graphic_column] eq "")) {
          $page_data .= "  <td align=\"center\">Sorry, no image is available.</td>\n";
        }
        elsif ($config{'show_graphic'} eq "yes") {
          $page_data .= "  <td align=\"center\"><img src=\"$config{'image_folder'}/$array[$graphic_column]\"></td>\n";
        }
        $page_data .= "    <td align=\"center\"><input type=\"hidden\" name=\"item$i\" value=\"$array[0]\">$array[3]"; # item SKU & description

        # display product's long description
        if (($config{'show_long_description'} eq "yes") && ($array[$long_description_column] ne "") && ($long_description_column ne "")) {
          $page_data .= "<br>$array[$long_description_column]\n";
        }

        # display product's weight
        if (($config{'show_weight'} eq "yes") && ($array[$weight_column] ne "") && ($weight_column ne "")) {
          $page_data .= "<br>Weight: $array[$weight_column] Lbs.\n";
        }

        # display product attribute options
        if (($array[$descra_column] =~ /\w/) && ($descra_column ne "")) {
          my @descra_temp = split(/\:/, $array[$descra_column], 2);
          my @descra_temp2 = split(/\|/, $descra_temp[1]);
          $page_data .= "<br>$descra_temp[0]\: <select name=\"descra$i\">\n";
          for (my $a = 0; $a <= $#descra_temp2; $a++) {
            $page_data .= "<option value=\"$descra_temp2[$a]\">$descra_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrb_column] =~ /\w/) && ($descrb_column ne "")) {
          my @descrb_temp = split(/\:/, $array[$descrb_column], 2);
          my @descrb_temp2 = split(/\|/, $descrb_temp[1]);
          $page_data .= "<br>$descrb_temp[0]\: <select name=\"descrb$i\">\n";
          for (my $a = 0; $a <= $#descrb_temp2; $a++) {
            $page_data .= "<option value=\"$descrb_temp2[$a]\">$descrb_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrc_column] =~ /\w/) && ($descrc_column ne "")) {
          my @descrc_temp = split(/\:/, $array[$descrc_column], 2);
          my @descrc_temp2 = split(/\|/, $descrc_temp[1]);
          $page_data .= "<br>$descrc_temp[0]\: <select name=\"descrc$i\">\n";
          for (my $a = 0; $a <= $#descrc_temp2; $a++) {
            $page_data .= "<option value=\"$descrc_temp2[$a]\">$descrc_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }

        $page_data .= "</td>\n";
        $page_data .= "    <td align=\"center\">\$$array[1]</td>\n";
        if ($config{'show_shipping'} ne "no") {
          $page_data .= "    <td align=\"center\">\$$array[2]</td>\n";
        }

        $page_data .= "    <td align=\"center\">";
        if (($array[$instock_column] =~ /n/i) && ($instock_column ne "") && ($config{'allow_outofstock_orders'} eq "yes") && ($config{'checkstock'} ne "yes")) {
          $page_data .= "<i>This item is<br>back ordered.</i>\n";
          $page_data .= "<br><input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
        }
        elsif (($array[$instock_column] =~ /n/i) && ($instock_column ne "")) {
          $page_data .= "Sorry, this item<br>is not in stock.\n";
        }
        else {
          if ($array[0] =~ /.($config{'digital_download_extensions'})$/i) {
            $page_data .= "<input type=\"checkbox\" name=\"quantity$i\" value=\"1\"> Check To Add\n";
          }
          else {
            $page_data .= "<input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
          }
        }
        $page_data .= "</td>\n";

        $page_data .= "  </tr>\n";
      }
    }
    close(DATABASE);

    $page_data .= "</table>\n";
  }  # End tabled form format

  ### begin plain text format
  if ($config{'format'} eq "plain_text") {
    open(DATABASE, "$data_folder/orderfrm.prices") or print "Can't open $data_folder/orderfrm.prices for reading. $!";
    while(<DATABASE>) {
      chop;
      $theline = $_;

      if ($theline =~ m/\t/) {
        $theline =~ s/\"//g;
        @array = split(/\t/, $theline);
      }
      else {
        @array = split(/\"\,\"/, $theline);
        $array[0] =~ s/\"//g;
        $array[$#array] =~ s/\"//g;
      }

      if ($array[0] =~ /header /) {
        for (my $aaa = 0; $aaa <= $#array; $aaa++) {
          &assign_columns("$array[$aaa]", "$aaa");
        }
      }

      # produce hash of category names here
      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        my $category_name = $array[$category_column];
        $category_name =~ s/ /\_/g;
        $category_name =~ s/\W//g; # remove non-allowed characters
        #$category_name =~ s/(\r|\n|\r\n|\n\r)//g; # remove new lines & carriage returns
        if ($category_name eq "") {
          $category_name = "Uncategorized";
        }
        $category_hash{"$category_name"} = $category_hash{"$category_name"} + 1;
      }

      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && ($array[$category_column] =~ /^$query{'category'}/i) && ($array[0] eq "$query{'sku'}") && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        $i++;
        $page_data .= "<p>\n";
        if (($config{'show_graphic'} eq "yes") && ($array[$graphic_column] eq "")) {
          $page_data .= "<br>Sorry, no image is available.\n";
        }
        elsif ($config{'show_graphic'} eq "yes") {
          $page_data .= "<br><img src=\"$config{'image_folder'}/$array[$graphic_column]\">\n";
        }
        $page_data .= "<input type=\"hidden\" name=\"item$i\" value=\"$array[0]\">\n"; # item SKU
        $page_data .= "<br><b>$array[3]</b>\n"; # description

        # display product's long description
        if (($config{'show_long_description'} eq "yes") && ($array[$long_description_column] ne "") && ($long_description_column ne "")) {
          $page_data .= "<br>$array[$long_description_column]\n";
        }

        # display product's weight
        if (($config{'show_weight'} eq "yes") && ($array[$weight_column] ne "") && ($weight_column ne "")) {
          $page_data .= "<br>Weight: $array[$weight_column] Lbs.\n";
        }

        # display product attribute options
        if (($array[$descra_column] =~ /\w/) && ($descra_column ne "")) {
          my @descra_temp = split(/\:/, $array[$descra_column], 2);
          my @descra_temp2 = split(/\|/, $descra_temp[1]);
          $page_data .= "<br>$descra_temp[0]\: <select name=\"descra$i\">\n";
          for (my $a = 0; $a <= $#descra_temp2; $a++) {
            $page_data .= "<option value=\"$descra_temp2[$a]\">$descra_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrb_column] =~ /\w/) && ($descrb_column ne "")) {
          my @descrb_temp = split(/\:/, $array[$descrb_column], 2);
          my @descrb_temp2 = split(/\|/, $descrb_temp[1]);
          $page_data .= "<br>$descrb_temp[0]\: <select name=\"descrb$i\">\n";
          for (my $a = 0; $a <= $#descrb_temp2; $a++) {
            $page_data .= "<option value=\"$descrb_temp2[$a]\">$descrb_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrc_column] =~ /\w/) && ($descrc_column ne "")) {
          my @descrc_temp = split(/\:/, $array[$descrc_column], 2);
          my @descrc_temp2 = split(/\|/, $descrc_temp[1]);
          $page_data .= "<br>$descrc_temp[0]\: <select name=\"descrc$i\">\n";
          for (my $a = 0; $a <= $#descrc_temp2; $a++) {
            $page_data .= "<option value=\"$descrc_temp2[$a]\">$descrc_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }

        $page_data .= "<br>Price: \$$array[1]\n";
        if ($config{'show_shipping'} ne "no") {
          $page_data .= "<br>Shipping: \$$array[2]\n";
        }

        if (($array[$instock_column] =~ /n/i) && ($instock_column ne "") && ($config{'allow_outofstock_orders'} eq "yes") && ($config{'checkstock'} ne "yes")) {
          $page_data .= "<br><i>This item is back ordered.</i>\n";
          $page_data .= "<br>Quantity: <input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
        }
        elsif (($array[$instock_column] =~ /n/i) && ($instock_column ne "")) {
          $page_data .= "<br>Sorry, this item is not in stock.\n";
        }
        else {
          if ($array[0] =~ /.($config{'digital_download_extensions'})$/i) {
            $page_data .= "<input type=\"checkbox\" name=\"quantity$i\" value=\"1\"> Check To Add\n";
          }
          else {
            $page_data .= "<input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
          }
        }
      }
    }
  }  # End plain text format

  $page_data .= "<p><input type=\"submit\" value=\"Add To Cart\" name=\"order\"> \&nbsp; <input type=\"reset\" value\=\"Reset Form\">\n";
  $page_data .= "</form>\n";

  $page_data .= "<p><form method=\"post\" action=\"$script\">\n";
  $page_data .= "<input type=\"submit\" value=\"Catalog Main Menu\">\n";
  $page_data .= "</form>\n";

  $page_data .= "<form method=\"post\" action=\"http://$config{'payment_gateway_domain'}/easycart.cgi\">\n";
  $page_data .= "<input type=\"hidden\" name=\"username\" value=\"$config{'merchant'}\">\n";
  $page_data .= "<input type=\"hidden\" name=\"function\" value=\"checkout\">\n";
  $page_data .= "<input type=\"hidden\" name=\"ec_version\" value=\"$config{'ec_version'}\">\n";
  if ($config{'continue'} ne "") {
    $page_data .= "<input type=\"hidden\" name=\"continue\" value=\"$config{'continue'}\">\n";
  }
  $page_data .= "<input type=\"submit\" value=\"View Shopping Cart\">\n";
  $page_data .= "</form>\n";

  $page_data .= "</div>\n";


  # make necessary forms
  my $search_form = &create_search_form();
  my $checkout_form .= &create_checkout_form();
  my $menu_row_form = &create_menu_row_form(%category_hash);
  my $menu_column_form = &create_menu_column_form(%category_hash);

  # send page to screen
  open(TEMPLATE, "$data_folder/template_category.htm") or print "Cannot open $data_folder/template_category.htm for reading. $!\n";
  while(<TEMPLATE>) {
    $theline = $_;

    if ($theline =~ /\[table\]/) {
      $theline =~ s/\[table\]/$page_data/g;
    }

    if ($theline =~ /\[search\]/) {
      $theline =~ s/\[search\]/$search_form/g;
    }

    if ($theline =~ /\[checkout\]/) {
      $theline =~ s/\[checkout\]/$checkout_form/g;
    }

    if ($theline =~ /\[menu_row\]/) {
      $theline =~ s/\[menu_row\]/$menu_row_form/g;
    }

    if ($theline =~ /\[menu_column\]/) {
      $theline =~ s/\[menu_column\]/$menu_column_form/g;
    }

    print $theline;
  }
  close(TEMPLATE);

  return;
}

sub download_update {
  &html_head();

  my $database_URL = "http://$config{'payment_gateway_domain'}/catalog_retrieve.cgi\?merchant=$config{'merchant'}"; # set URL to database file on PnP server

  #retrieve this web page
  my $database_data = get($database_URL);

  open(DATABASE, ">$data_folder/orderfrm.prices") or print "Cannot open $data_folder/orderfrm.prices for writing. $!\n";
  print DATABASE $database_data;
  close(DATABASE);

  print "<br><b>EasyCart Online Catalog Database Updated...</b>\n";
  print "<br>Merchant = $config{'merchant'}\n";

  print "<p>* Note: If you do not see your EasyCart updates below, press the 'Refresh' button in your browser's navigation menu to see the update.\n";

  print "<p><pre>\n";
  print $database_data;
  print "</pre>\n";

  print "<p><form method=\"post\" action=\"$script\">\n";
  print "<input type=\"submit\" value=\"Catalog Main Menu\">\n";
  print "</form>\n";

  &html_tail();
  return;
}

sub run_test {
  &html_head();

  print "<b>EASYCART CATALOG CHECK-UP:</B><br>\n";
  print "<br>* Note: To see any newly updated settings, press the 'Refresh' button in your browser's navigation menu.\n";

  print "<p><hr>\n";

  print "<p>FILE ACCESS CHECK:<br>\n";
  print "<br>EasyCart Catalog Config: \n";
  if (!-r "$data_folder/config.txt") {
    print "<br>-- No Read Permission\n";
  }
  else {
    print "<br>-- File OK\n";
  }

  print "<br>EasyCart Catalog Database: \n";
  if (!-r "$data_folder/orderfrm.prices") {
    print "<br>-- No Read Permission\n";
  }
  elsif (!-w "$data_folder/orderfrm.prices") {
    print "<br>-- No Write Permission\n";
  }
  else {
    print "<br>-- File OK\n";
  }

  print "<br>Main Template: \n";
  if (!-r "$data_folder/template_main.htm") {
    print "<br>-- No Read Permission\n";
  }
  else {
    print "<br>-- File OK\n";
  }

  print "<br>Category Template: \n";
  if (!-r "$data_folder/template_category.htm") {
    print "<br>-- No Read Permission\n";
  }
  else {
    print "<br>-- File OK\n";
  }

  print "<br>Category Template: \n";
  if (!-r "$data_folder/template_orderform.htm") {
    print "<br>-- No Read Permission\n";
  }
  else {
    print "<br>-- File OK\n";
  }

  print "<p><hr>\n";

  print "<p>SCRIPT SETTINGS/OPTIONS:<br>\n";
  print "<br><table border=1>\n";

  foreach my $key (sort keys %config) {
    print "  <tr>\n";
    print "    <th bgcolor=#eeeeee>$key</th>\n";
    print "    <td>$config{$key}</td>\n";
    print "  </tr>\n";
  }

  print "</table>\n";

  print "<p><hr>\n";

  #print "<p>SERVER ENVIRONMENT INFO:<br>\n";
  #foreach my $var (sort keys %ENV) {
  #  print "<br>$var = $ENV{\"$var\"}\n";
  #}

  &html_tail();
  return;
}


sub html_head {
  print "<html>\n";
  print "<head>\n";
  print "<META HTTP-EQUIV=\"CACHE-CONTROL\" CONTENT=\"NO-CACHE\">\n"; # turns off browser cache of web page
  print "<META HTTP-EQUIV=\"PRAGMAS\" CONTENT=\"NO-CACHE\">\n";       # turns off browser cache of web page
  print "<title>EasyCart Online Catalog</title>\n";
  print "</head>\n";
  print "<body>\n";
  return;
}


sub html_tail {
  print "</body>\n";
  print "</html>\n";
  return;
}

sub create_search_form {
  # make search form code
  my $search_form = "<form method=\"post\" action=\"$script\">\n";
  $search_form .= "<input type=\"hidden\" name=\"mode\" value=\"search\">\n";
  $search_form .= "<input type=\"text\" name=\"search_for\" value=\"\" size=\"20\">\n";
  $search_form .= "<input type=\"submit\" value=\"Search\">\n";
  $search_form .= "</form>\n";

  return $search_form;
}

sub create_checkout_form {
  # make checkout form code
  my $checkout_form .= "<form method=\"post\" action=\"http://$config{'payment_gateway_domain'}/easycart.cgi\">\n";
  $checkout_form .= "<input type=\"hidden\" name=\"username\" value=\"$config{'merchant'}\">\n";
  $checkout_form .= "<input type=\"hidden\" name=\"function\" value=\"checkout\">\n";
  $checkout_form .= "<input type=\"hidden\" name=\"ec_version\" value=\"$config{'ec_version'}\">\n";
  if ($config{'continue'} ne "") {
    $checkout_form .= "<input type=\"hidden\" name=\"continue\" value=\"$config{'continue'}\">\n";
  }
  $checkout_form .= "<input type=\"submit\" value=\"Checkout\">\n";
  $checkout_form .= "</form>\n";

  return $checkout_form;
}

sub create_menu_row_form {
  my %category_hash = @_;

  # make menu row code here
  my $menu_row_form;
  foreach my $key (sort keys %category_hash) {
    my $category_name = $key;
    $category_name =~ s/\_/ /g;
    $category_name = uc("$category_name");
    $menu_row_form .= "&bull; <a href=\"$script\?mode=show_category\&category=$key\"><b>$category_name</b></a> &nbsp;";
  }
  $menu_row_form .= "&bull\n";

  return $menu_row_form;
}

sub create_menu_column_form {
  my %category_hash = @_;

  # make menu column code here
  my $menu_column_form;
  foreach my $key (sort keys %category_hash) {
    my $category_name = $key;
    $category_name =~ s/\_/ /g;
    $category_name = uc("$category_name");
    $menu_column_form .= "<nobr>&bull; <a href=\"$script\?mode=show_category\&category=$key\"><b>$category_name</b></a>";
    if ($config{'category_count'} eq "yes") {
      $menu_column_form .= sprintf(" [%d]", $category_hash{$key});
    }
    $menu_column_form .= "</nobr><br>\n";
  }

  $menu_column_form .= "<p><a href=\"$script\"><nobr><b>Catalog Main Menu</b><nobr></a>\n";
  $menu_column_form .= "<br><a href=\"http://$config{'payment_gateway_domain'}/easycart.cgi\?username=$config{'merchant'}\&function=checkout\&ec_version=$config{'ec_version'}\"><nobr><b>View Shopping Cart</b></nobr></a>\n";

  return $menu_column_form;
}

sub assign_columns {
  my ($name, $pos) = @_;

  # figure out what column category is
  if ($name =~ /category/i) {
    $category_column = $pos;
  }

  # figure out what column site is
  elsif ($name =~ /site/i) {
    $site_column = $pos;
  }

  # figure out what column graphic is
  elsif ($name =~ /graphic/i) {
    $graphic_column = $pos;
  }

  # figure out what columns the product attributes are
  elsif ($name =~ /descra/i) {
    $descra_column = $pos;
  }
  elsif ($name =~ /descrb/i) {
    $descrb_column = $pos;
  }
  elsif ($name =~ /descrc/i) {
    $descrc_column = $pos;
  }

  # figure out what column instock is
  elsif ($name =~ /instock/i) {
    $instock_column = $pos;
  }

  # figure out what column weight is
  elsif ($name =~ /weight/i) {
    $weight_column = $pos;
  }

  # figure out what column long_description is
  elsif ($name =~ /long_description/i) {
    $long_description_column = $pos;
  }

  else {
    # its noting we need to be concerned with
    # so just skip it
  }

  return;
}

sub search {
  my ($page_data, $search_for);
  my %category_hash;

  # clean-up
  $query{'search_for'} =~ s/\W/ /g; # replace non-alphanumeric characters with spaces
  $query{'search_for'} =~ s/( ){2,}/ /g; # replace all instances of 2 or more spaces with a single space
  $query{'search_for'} =~ s/ /\|/g; # replace each single space with a pipe

  if ($config{'format'} eq "no_border_table") {
    $query{'view_border'} = "0";  # table with no borders
  }
  elsif ($config{'format'} eq "border_table") {
    $query{'view_border'} = "1";  # table with borders
  }
  elsif ($config{'format'} eq "plain_text") {
    $query{'view_border'} = "1";  # plan text - no tables
  }

  $page_data .= "<div align=\"center\">\n";

  $page_data .= "<form name=\"ezcart\" action=\"http://$config{'payment_gateway_domain'}/easycart.cgi\" method=\"post\">\n";
  $page_data .= "<input type=\"hidden\" name=\"username\" value=\"$config{'merchant'}\">\n";
  $page_data .= "<input type=\"hidden\" name=\"function\" value=\"add\">\n";
  $page_data .= "<input type=\"hidden\" name=\"ec_version\" value=\"$config{'ec_version'}\">\n";

  if ($config{'checkstock'} eq "yes") {
    $page_data .= "<input type=\"hidden\" name=\"checkstock\" value=\"yes\">\n";
  }

  if ($config{'continue'} ne "") {
    $page_data .= "<input type=\"hidden\" name=\"continue\" value=\"$config{'continue'}\">\n";
  }

  ### For table form format
  if (($config{'format'} eq "no_border_table") || ($config{'format'} eq "border_table")) {
    $page_data .= "<table border=\"$query{'view_border'}\" width=\"75\%\">\n";
    $page_data .= "  <tr>\n";
    if ($config{'show_graphic'} eq "yes") {
      $page_data .= "    <th>&nbsp;</th>\n";
    }
    $page_data .= "    <th>Product Description</th>\n";
    $page_data .= "    <th>Price</th>\n";
    if ($config{'show_shipping'} ne "no") {
      $page_data .= "    <th>Shipping</th>\n";
    }
    $page_data .= "    <th>Quantity</th>\n";
    $page_data .= "  </tr>\n";

    open(DATABASE, "$data_folder/orderfrm.prices") or print "Can't open $data_folder/orderfrm.prices for reading. $!";
    while(<DATABASE>) {
      chop;
      $theline = $_;

      if ($theline =~ m/\t/) {
        $theline =~ s/\"//g;
        @array = split(/\t/, $theline);
      }
      else {
        @array = split(/\"\,\"/, $theline);
        $array[0] =~ s/\"//g;
        $array[$#array] =~ s/\"//g;
      }

      if ($array[0] =~ /header /) {
        for (my $aaa = 0; $aaa <= $#array; $aaa++) {
          &assign_columns("$array[$aaa]", "$aaa");
        }
      }

      # produce hash of category names here
      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        my $category_name = $array[$category_column];
        $category_name =~ s/ /\_/g;
        $category_name =~ s/\W//g; # remove non-allowed characters
        #$category_name =~ s/(\r|\n|\r\n|\n\r)//g; # remove new lines & carriage returns
        if ($category_name eq "") {
          $category_name = "Uncategorized";
        }
        $category_hash{"$category_name"} = $category_hash{"$category_name"} + 1;
      }

      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && ($array[3] =~ /$query{'search_for'}/i) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        $i++;
        $page_data .= "  <tr>\n";
        if (($config{'show_graphic'} eq "yes") && ($array[$graphic_column] eq "")) {
          $page_data .= "  <td align=\"center\">Sorry, no image is available.</td>\n";
        }
        elsif ($config{'show_graphic'} eq "yes") {
          $page_data .= "  <td align=\"center\"><img src=\"$config{'image_folder'}/$array[$graphic_column]\"></td>\n";
        }
        $page_data .= "    <td align=\"center\"><input type=\"hidden\" name=\"item$i\" value=\"$array[0]\">$array[3]"; # item SKU & description

        # display product's long description
        if (($config{'show_long_description'} eq "yes") && ($array[$long_description_column] ne "") && ($long_description_column ne "")) {
          $page_data .= "<br>$array[$long_description_column]\n";
        }

        # display product's weight
        if (($config{'show_weight'} eq "yes") && ($array[$weight_column] ne "") && ($weight_column ne "")) {
          $page_data .= "<br>Weight: $array[$weight_column] Lbs.\n";
        }

        # display product attribute options
        if (($array[$descra_column] =~ /\w/) && ($descra_column ne "")) {
          my @descra_temp = split(/\:/, $array[$descra_column], 2);
          my @descra_temp2 = split(/\|/, $descra_temp[1]);
          $page_data .= "<br>$descra_temp[0]\: <select name=\"descra$i\">\n";
          for (my $a = 0; $a <= $#descra_temp2; $a++) {
            $page_data .= "<option value=\"$descra_temp2[$a]\">$descra_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrb_column] =~ /\w/) && ($descrb_column ne "")) {
          my @descrb_temp = split(/\:/, $array[$descrb_column], 2);
          my @descrb_temp2 = split(/\|/, $descrb_temp[1]);
          $page_data .= "<br>$descrb_temp[0]\: <select name=\"descrb$i\">\n";
          for (my $a = 0; $a <= $#descrb_temp2; $a++) {
            $page_data .= "<option value=\"$descrb_temp2[$a]\">$descrb_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrc_column] =~ /\w/) && ($descrc_column ne "")) {
          my @descrc_temp = split(/\:/, $array[$descrc_column], 2);
          my @descrc_temp2 = split(/\|/, $descrc_temp[1]);
          $page_data .= "<br>$descrc_temp[0]\: <select name=\"descrc$i\">\n";
          for (my $a = 0; $a <= $#descrc_temp2; $a++) {
            $page_data .= "<option value=\"$descrc_temp2[$a]\">$descrc_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }

        $page_data .= "</td>\n";
        $page_data .= "    <td align=\"center\">\$$array[1]</td>\n";
        if ($config{'show_shipping'} ne "no") {
          $page_data .= "    <td align=\"center\">\$$array[2]</td>\n";
        }

        $page_data .= "    <td align=\"center\">";
        if (($array[$instock_column] =~ /n/i) && ($instock_column ne "") && ($config{'allow_outofstock_orders'} eq "yes") && ($config{'checkstock'} ne "yes")) {
          $page_data .= "<i>This item is<br>back ordered.</i>\n";
          $page_data .= "<br><input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
        }
        elsif (($array[$instock_column] =~ /n/i) && ($instock_column ne "")) {
          $page_data .= "Sorry, this item<br>is not in stock.\n";
        }
        else {
          if ($array[0] =~ /\.($config{'digital_download_extensions'})$/i) {
            $page_data .= "<input type=\"checkbox\" name=\"quantity$i\" value=\"1\"> Check To Add\n";
          }
          else {
            $page_data .= "<input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
          }
        }
        $page_data .= "</td>\n";

        $page_data .= "  </tr>\n";
      }
    }
    close(DATABASE);

    $page_data .= "</table>\n";
  }  # End tabled form format

  ### begin plain text format
  if ($config{'format'} eq "plain_text") {
    open(DATABASE, "$data_folder/orderfrm.prices") or print "Can't open $data_folder/orderfrm.prices for reading. $!";
    while(<DATABASE>) {
      chop;
      $theline = $_;

      if ($theline =~ m/\t/) {
        $theline =~ s/\"//g;
        @array = split(/\t/, $theline);
      }
      else {
        @array = split(/\"\,\"/, $theline);
        $array[0] =~ s/\"//g;
        $array[$#array] =~ s/\"//g;
      }

      if ($array[0] =~ /header /) {
        for (my $aaa = 0; $aaa <= $#array; $aaa++) {
          &assign_columns("$array[$aaa]", "$aaa");
        }
      }

      # produce hash of category names here
      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        my $category_name = $array[$category_column];
        $category_name =~ s/ /\_/g;
        $category_name =~ s/\W//g; # remove non-allowed characters
        #$category_name =~ s/(\r|\n|\r\n|\n\r)//g; # remove new lines & carriage returns
        if ($category_name eq "") {
         $category_name = "Uncategorized";
        }
        $category_hash{"$category_name"} = $category_hash{"$category_name"} + 1;
      }

      if (($array[0] =~ /\w/) && ($array[0] !~ /^(shipping|tax|cardtype|header) /) && ($array[3] =~ /$query{'search_for'}/i) && (($array[$site_column] =~ /$config{'match_site'}/) || ($config{'match_site'} eq ""))) {
        $i++;
        $page_data .= "<p>\n";
        if (($config{'show_graphic'} eq "yes") && ($array[$graphic_column] eq "")) {
          $page_data .= "<br>Sorry, no image is available.\n";
        }
        elsif ($config{'show_graphic'} eq "yes") {
          $page_data .= "<br><img src=\"$config{'image_folder'}/$array[$graphic_column]\">\n";
        }
        $page_data .= "<input type=\"hidden\" name=\"item$i\" value=\"$array[0]\">\n"; # item SKU
        $page_data .= "<br><b>$array[3]</b>\n"; # description

        # display product's long description
        if (($config{'show_long_description'} eq "yes") && ($array[$long_description_column] ne "") && ($long_description_column ne "")) {
          $page_data .= "<br>$array[$long_description_column]\n";
        }

        # display product's weight
        if (($config{'show_weight'} eq "yes") && ($array[$weight_column] ne "") && ($weight_column ne "")) {
          $page_data .= "<br>Weight: $array[$weight_column] Lbs.\n";
        }

        # display product attribute options
        if (($array[$descra_column] =~ /\w/) && ($descra_column ne "")) {
          my @descra_temp = split(/\:/, $array[$descra_column], 2);
          my @descra_temp2 = split(/\|/, $descra_temp[1]);
          $page_data .= "<br>$descra_temp[0]\: <select name=\"descra$i\">\n";
          for (my $a = 0; $a <= $#descra_temp2; $a++) {
            $page_data .= "<option value=\"$descra_temp2[$a]\">$descra_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrb_column] =~ /\w/) && ($descrb_column ne "")) {
          my @descrb_temp = split(/\:/, $array[$descrb_column], 2);
          my @descrb_temp2 = split(/\|/, $descrb_temp[1]);
          $page_data .= "<br>$descrb_temp[0]\: <select name=\"descrb$i\">\n";
          for (my $a = 0; $a <= $#descrb_temp2; $a++) {
            $page_data .= "<option value=\"$descrb_temp2[$a]\">$descrb_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }
        if (($array[$descrc_column] =~ /\w/) && ($descrc_column ne "")) {
          my @descrc_temp = split(/\:/, $array[$descrc_column], 2);
          my @descrc_temp2 = split(/\|/, $descrc_temp[1]);
          $page_data .= "<br>$descrc_temp[0]\: <select name=\"descrc$i\">\n";
          for (my $a = 0; $a <= $#descrc_temp2; $a++) {
            $page_data .= "<option value=\"$descrc_temp2[$a]\">$descrc_temp2[$a]</option>\n";
          }
          $page_data .= "</select>\n";
        }

        $page_data .= "<br>Price: \$$array[1]\n";
        if ($config{'show_shipping'} ne "no") {
          $page_data .= "<br>Shipping: \$$array[2]\n";
        }

        if (($array[$instock_column] =~ /n/i) && ($instock_column ne "") && ($config{'allow_outofstock_orders'} eq "yes") && ($config{'checkstock'} ne "yes")) {
          $page_data .= "<br><i>This item is back ordered.</i>\n";
          $page_data .= "<br>Quantity: <input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
        }
        elsif (($array[$instock_column] =~ /n/i) && ($instock_column ne "")) {
          $page_data .= "<br>Sorry, this item is not in stock.\n";
        }
        else {
          if ($array[0] =~ /.($config{'digital_download_extensions'})$/i) {
            $page_data .= "<input type=\"checkbox\" name=\"quantity$i\" value=\"1\"> Check To Add\n";
          }
          else {
            $page_data .= "<input type=\"text\" name=\"quantity$i\" value=\"\" size=\"3\">\n";
          }
        }
      }
    }
  }  # End plain text format

  $page_data .= "<p><input type=\"submit\" value=\"Add To Cart\" name=\"order\"> \&nbsp; <input type=\"reset\" value\=\"Reset Form\">\n";
  $page_data .= "</form>\n";

  $page_data .= "<p><form method=\"post\" action=\"$script\">\n";
  $page_data .= "<input type=\"submit\" value=\"Catalog Main Menu\">\n";
  $page_data .= "</form>\n";

  $page_data .= "<form method=\"post\" action=\"http://$config{'payment_gateway_domain'}/easycart.cgi\">\n";
  $page_data .= "<input type=\"hidden\" name=\"username\" value=\"$config{'merchant'}\">\n";
  $page_data .= "<input type=\"hidden\" name=\"function\" value=\"checkout\">\n";
  $page_data .= "<input type=\"hidden\" name=\"ec_version\" value=\"$config{'ec_version'}\">\n";
  if ($config{'continue'} ne "") {
    $page_data .= "<input type=\"hidden\" name=\"continue\" value=\"$config{'continue'}\">\n";
  }
  $page_data .= "<input type=\"submit\" value=\"View Shopping Cart\">\n";
  $page_data .= "</form>\n";

  $page_data .= "</div>\n";

  # make necessary forms
  my $search_form = &create_search_form();
  my $checkout_form .= &create_checkout_form();
  my $menu_row_form = &create_menu_row_form(%category_hash);
  my $menu_column_form = &create_menu_column_form(%category_hash);

  # send page to screen
  open(TEMPLATE, "$data_folder/template_orderform.htm") or print "Cannot open $data_folder/template_orderform.htm for reading. $!\n";
  while(<TEMPLATE>) {
    $theline = $_;

    if ($theline =~ /\[table\]/) {
      $theline =~ s/\[table\]/$page_data/g;
    }

    if ($theline =~ /\[search\]/) {
      $theline =~ s/\[search\]/$search_form/g;
    }

    if ($theline =~ /\[checkout\]/) {
      $theline =~ s/\[checkout\]/$checkout_form/g;
    }

    if ($theline =~ /\[menu_row\]/) {
      $theline =~ s/\[menu_row\]/$menu_row_form/g;
    }

    if ($theline =~ /\[menu_column\]/) {
      $theline =~ s/\[menu_column\]/$menu_column_form/g;
    }

    print $theline;
  }
  close(TEMPLATE);

  return;
}

