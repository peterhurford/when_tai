def nuclear_scenarios_module(y, state, verbose):
    peace = y < state['peace_until'] if state['peace_until'] is not None else False
    if sq.event_occurs(p_nuclear_accident(state['war'], y - CURRENT_YEAR)):
        if sq.event(p_nuclear_accident_becomes_exchange(state['war'])):
            state['nuclear_weapon_used'] = True
            if sq.event_occurs(p_catastrophe_from_nuclear_exchange(state['war'])):
                if sq.event_occurs(p_xrisk_from_nuclear_catastrophe):
                    if verbose:
                        print('{}: ...XRISK from nukes (accidental exchange) :('.format(y))
                    state['category'] = 'xrisk_nukes_accident'
                    state['terminate'] = True; state['final_year'] = y
                else:    
                    if verbose:
                        print('{}: ...catastrophe from nukes (accidental exchange)'.format(y))
                    state['catastrophe'].append('nukes_accident')
    
    first_year_of_war = state['war'] and (state['war_start_year'] == y)
    if not state['terminate'] and state['war'] and sq.event_occurs(p_nuclear_exchange_given_war(first_year_of_war)):
        state['nuclear_weapon_used'] = True
        if sq.event_occurs(p_catastrophe_from_nuclear_exchange(state['war'])):
            if sq.event_occurs(p_xrisk_from_nuclear_catastrophe):
                if verbose:
                    print('{}: ...XRISK from nukes (war) :('.format(y))
                state['category'] = 'xrisk_nukes_war'
                state['terminate'] = True; state['final_year'] = y
            else:    
                if verbose:
                    print('{}: ...catastrophe from nukes (war)'.format(y))
                state['catastrophe'].append('nukes_war')
    
    if not state['terminate'] and not state['war'] and sq.event(p_russia_uses_nuke(peace, y - CURRENT_YEAR)):
        if verbose:
            print('{}: Russia uses a nuke first strike (outside of great power war)!'.format(y))
        state['nuclear_weapon_used'] = True
        state['russia_nuke_first'] = True
        
    if not state['terminate'] and sq.event(p_nk_uses_nuke):
        if verbose:
            print('{}: North Korea uses a nuke first strike!'.format(y))
        state['nuclear_weapon_used'] = True
    
    if not state['terminate'] and not state['war'] and sq.event(p_other_uses_nuke(peace)):
        if verbose:
            print('{}: A country other than Russia uses a nuke first strike (outside of great power war)!'.format(y))
        state['nuclear_weapon_used'] = True
                
    return state