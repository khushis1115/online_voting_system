def tally_votes(chain):
    unique_votes = set()
    for block in chain:
        vote_data = block.data['vote_hash']
        if vote_data in unique_votes:
            return 'Duplicate vote detected.'
        unique_votes.add(vote_data)
    return f'Total votes tallied: {len(unique_votes)}'
