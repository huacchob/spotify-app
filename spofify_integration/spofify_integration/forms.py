from django import forms


class TrackArtistForm(forms.Form):
    artist = forms.CharField(
        max_length=100,
        label="Artist Name",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter artist name", "class": "form-control"}
        ),
    )
    track_name = forms.CharField(
        max_length=100,
        label="Track Name",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter track name", "class": "form-control"}
        ),
    )


class ArtistForm(forms.Form):
    artist = forms.CharField(
        max_length=100,
        label="Artist Name",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter artist name", "class": "form-control"}
        ),
    )
