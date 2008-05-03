// web_nutrition: a web based nutrition and diet analysis program.
// Copyright (C) 2008 Edgar Denny

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

// When the page is ready

$(document).ready(function(){
        $("#tabs div").each(function(){
                $(this).hide();
            });
        $("#tabs div:first").show();
        $("#nav a:first").addClass("activetab");
        $("#nav a").click(function(){
                var AttrTitle = $(this).attr("title");
                $("#nav a").each(function(){
                        if ( $(this).hasClass("activetab")){
                            $(this).removeClass("activetab");
                        }
                    });
                $(this).addClass("activetab");
                $("#tabs div").each(function(){
                        var AttrId = $(this).attr("id");
                        if (AttrTitle == AttrId) {
                            $(this).show();
                        } else {
                            $(this).hide();
                        }
                    });
            });
    });
