import json
import numpy as np

N_INV_SLOTS = 41

with open('data/mc_item_ids.json', 'r') as f:
    item_ids = json.load(f)

# Convert to one hot format
def to_oh(idx, n):
    arr = np.zeros(n)
    arr [idx] = 1
    return arr

def check_oh(l):
    one_count = 0
    for item in l:
        if item == 1:
            if one_count >= 1:
                return False
            elif one_count == 0:
                one_count += 1
        elif item != 0:
            return False

    if one_count == 1:
        return True
    return False

def preprocess_state(state, agent_spec, flat=False, incl_chat=True, idx=-1):
    state_dict = {}
    try:
        vid = state.video_frames[idx]

        pixels = np.frombuffer(vid.pixels, dtype=np.int8)
        pixels = pixels.astype(np.float32)
        pixels += 128
        pixels /= 255.

        if agent_spec.observation_space == 0:
            pixels = pixels.reshape(agent_spec.observation_dim + (3,))
        else:
            pixels = pixels.reshape(agent_spec.observation_dim + (4,))

        state_dict['pixels'] = pixels
    except IndexError:
        print('There was no video at the given index since ', 
            'the previous update, so preprocess_state returned `None`')
        return None

    if agent_spec.observation_space >= 1:
        try:
            obs = json.loads(state.observations[idx].text)
        except IndexError:
            print('There were no observations at the given index since ', 
                'the previous update, so preprocess_state returned `None`')
            return None

        # Inventory parsing
        inv_arr = []
        for i in range(N_INV_SLOTS):
            inv_arr.append(obs[f'InventorySlot_{i}_item'])
            inv_arr[-1] = item_ids[inv_arr[-1]] / 391.
            inv_arr.append(obs[f'InventorySlot_{i}_size'] / 64.)

        state_dict['inventory'] = np.array(inv_arr)

        # Stats parsing
        stats_arr = []
        curr_item_idx = to_oh(obs['currentItemIndex'], 9)
        stats_arr.extend(curr_item_idx)
        
        stats_arr.append(obs['Life'] / 20.)
        stats_arr.append(obs['Food'] / 20.)
        stats_arr.append(obs['XP'] / 10000.)
        stats_arr.append(int(obs['IsAlive']))

        state_dict['stats'] = np.array(stats_arr)

    # Chat parsing
    if incl_chat and agent_spec.enable_chat:
        try:
            obs = json.loads(state.observations[idx].text)
            state_dict['chat'] = obs['Chat']
        except IndexError:
            state_dict['chat'] = []

    if not flat:
        return state_dict
    else:
        new_dict = {}
        if incl_chat:
            new_dict['chat'] = state_dict['chat']
        if agent_spec.observation_space >= 0:
            new_dict['pixels'] = state_dict['pixels']
        if agent_spec.observation_space >= 1:
            new_dict['other'] = np.concatenate(
                [state_dict['inventory'], state_dict['stats']])

        return new_dict
