This webapp is a jobs board for rock bands.

It allows the users to create "listings" for their bands in hopes that
other musicians will find the listing and "audition" for the band.

Here's a glossary of important terms:
- listing: analogous to a job posting on normal job boards. A listing 
    is created by a band looking for new members. A listing specifies
    desired roles to be filled and genres that describe the band.

- band: a user who created a listing.

- audition: analogous to a job application on a normal job board. A 
    user looking to join a band auditions for a listing.

- auditionee: a user who created an audition.

- role: basically an instrument, e.g. guitar, drums, keyboard. listings
     and auditions each have roles associated with them. If a listing
    has the roles "guitar, bass" then the band needs a guitarist and a
    bassist. If an audition has the roles "guitar, keyboard" the user
    is indicating that they are capable and interested in playing that
    instrument.

--Using the app--

The home page displays every listing, with the most recent on top.A button
to post a new listing is at the top of the page. A search bar with two 
forms, city and role, is underneath.Users can enter cities and/or a 
comma-separated list of roles. Pressing 'Submit' will refresh the page 
with only listings that match the given criteria. If the user enters 
"Chicago" and "guitar,bass" then only listings in Chicago that are looking 
for a guitarist or bassist will be listed. Clicking on the title of one of 
the listings will bring you to its page. 

The listing page displays all of the information about the listing:
all genres, roles, a description of the band, and audio samples (if
provided). A list of all auditions for the listing is displayed if 
the listing was created by the current user. Otherwise, a button to
audition for the band appears.

An audition is viewable only by the auditionee and the band who created
their audition's parent listing. The audition page displays information
similar to the listing page: a description of the auditionee, genres,
roles, and audio samples as well as an email address for the band to
contact the auditionee directly.

The page for creating a listing is a form that allows a band to enter
a title, their city, a description of the band, roles needed, genres,
and an audio sample. Multiple roles and genres can be entered through
the form. 

The page for creating an audition is reached through a listing. The 
form is similar to that of the listing. Roles are chosen from checkboxes
so that an auditionee cannot audition for an undesired role. 

If only one role or genre is entered in either form, the user must press 
enter or the + button next to the text field before submitting. Failure 
to do so will result in strange behavior. For example: if 'guitar' is 
entered as a role without opening a second text field, the resulting 
audition will list the roles [g,u,i,t,a,r]. This may be the result of a
bug in web2py's 'list:reference' field.

--Databases--

The application relies on 9 tables besides the auth tables.

- listing
    -title
    -city
    -created_by
    -date_created
    -body (the description of the band)

-audition
    -parent_ndx, reference listing
    -created_by
    -date_created
    -body (the description of the auditionee)
    
- genre
    -genre_name

- listing_genre
    -listing_ndx, references listing
    -genre_ndx, references genre

- audition_genre
    -audition_ndx, references audition
    -genre_ndx, references genre

- role
    -role_name

- listing_role
    -listing_ndx, references listing
    -role_ndx, references role

- audition_role
    -audition_ndx, references audition
    -role_ndx, references role

- audio_file
    -created_by
    -listing_ndx, references listing
    -audition_ndx, references audition
    -audio, path to the audio file
    
listing_genre, listing_role, audition_genre, and audition_role are all
used to map multiple possible roles or genres to a single audition or
role. This is to prevent multiple entries of common genres or roles 
such as 'guitarist' or 'rock' 

An audio_file row can reference a listing or an audition. There's
currently no way for it to reference both. There is no mapping 
table similar because it would be more difficult to compare files.

Developed with web2py.
