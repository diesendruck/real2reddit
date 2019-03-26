import argparse
import pdb
import praw
import requests
import requests.auth
import sys


STATE_ABBREVIATIONS = [
    'AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
    'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
    'MI', 'MN', 'MO', 'MP', 'MS', 'MT', 'NA', 'NC', 'ND', 'NE', 'NH', 'NJ',
    'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN',
    'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY']

parser = argparse.ArgumentParser()
parser.add_argument('--url', type=str, required=True)
args = vars(parser.parse_args())


def authenticate():
    client_auth = requests.auth.HTTPBasicAuth(
        CLIENT_ID,
        CLIENT_SECRET)

    post_data = {
        'grant_type': 'password',
        'username': USERNAME,
        'password': PASSWORD}

    headers = {"User-Agent": USER_AGENT}

    response = requests.post(
        'https://www.reddit.com/api/v1/access_token',
        auth=client_auth,
        data=post_data,
        headers=headers)

    request_token_result = response.json()

    if VERBOSE:
        print(request_token_result)

    headers = {
        'Authorization': 'bearer {}'.format(
            request_token_result['access_token']),
        'User-Agent': USER_AGENT}

    response = requests.get(
        'https://oauth.reddit.com/api/v1/me',
        headers=headers)

    use_token_result = response.json()
    if VERBOSE:
        print(use_token_result)


def get_id_from_redfin_url(url):
    url_tail = url.split('www.redfin.com/')[1].split('/home')[0]

    # Check for correct Redfin url (listing page).
    if url_tail[:2] not in STATE_ABBREVIATIONS:
        sys.exit('URL format not recognized as a listing page.')

    # e.g. url_tail = 'CA/Oakland/66-Fairmount-Ave-94611/unit-412'
    address_portion = url_tail.split('/')
    state = address_portion[0]
    city = address_portion[1]
    zipcode = address_portion[2][-5:]
    number = address_portion[2].split('-', 1)[0]
    street = address_portion[2].split('-', 1)[1][:-6]  # Cuts zipcode.
    has_unit = True if len(address_portion) == 4 else False
    if has_unit:
        unit = address_portion[3]
        listing_id = '-'.join([state, city, zipcode, number, street, unit])
    else:
        listing_id = '-'.join([state, city, zipcode, number, street])

    return listing_id


def get_id_from_url(url):
    if 'redfin' in url:
        listing_id = get_id_from_redfin_url(url)
    elif 'zillow' in url:
        sys.exit('TODO: Implement zillow links')

    else:
        sys.exit('TODO: Link is unknown')
    return listing_id


def listing_exists(url):
    """Checks if listing exists in file.

    Args:
      url: String, full url from site.

    Returns:
      exists: Boolean, whether id was found in file.
      line: String, from file if it was found.
    """
    listing_id = get_id_from_url(url)
    with open('listings.txt') as f:
        content = None
        for line in f:
            if listing_id in line:
                content = line
                break
        if content is not None:
            print('LISTING ALREADY EXISTS:\n  {}\n'.format(content))
        else:
            print('NO LISTING:\n  {}\n'.format(listing_id))

    exists = bool(content)
    return exists, content


def post(reddit, url):
    """Posts link to subreddit and logs the listing in text file.

    Args:
      reddit: Reddit instance.
      url: String, full url from site.

    Returns:
      out: Output from submission, containing submission identifier."""
    # Post the listing.
    listing_id = get_id_from_url(url)
    subreddit = reddit.subreddit(HOME_SUB)
    out = subreddit.submit(listing_id, url=url)

    # Write log entry.
    comment_url = (
        'https://www.reddit.com/r/{}/comments/{}/'.format(HOME_SUB, out.id))
    log_entry = '{},{}\n'.format(listing_id, comment_url)

    with open('listings.txt', 'a') as f:
        f.write(log_entry)

    print('ADDED LOG ENTRY and POSTED TO REDDIT:\n  {}\n'.format(log_entry))

    return out, log_entry


def main():
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        username=USERNAME,
        password=PASSWORD)

    exists, content = listing_exists(args['url'])

    if exists:
        print('Open {}'.format(content.split(',')[1]))
    if not exists:
        post(reddit, args['url'])

    # pdb.set_trace()


if __name__ == "__main__":
    main()
