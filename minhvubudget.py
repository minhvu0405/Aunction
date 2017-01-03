#!/usr/bin/env python

import sys
import math
from gsp import GSP
from util import argmax_index
from minhvubb import MinhVubb
class MinhVubudget(MinhVubb):
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget
    def initial_bid(self, reserve):
        return self.value / 2
    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
            
        info = map(compute, range(len(clicks)))
#        sys.stdout.write("slot info: %s\n" % info)
        return info


    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        # TODO: Fill this in
        utilities = []   # Change this
        slots = self.slot_info(t, history, reserve)
        previous = history.round(t-1)
        slotInfo = self.slot_info(t,history,reserve)
        clicks = [0]*len(previous.clicks)
        clicks[0] = int(round(30*math.cos(math.pi*t/24)+50))
        for i in range(1,len(previous.clicks)):
        	clicks[i] = clicks[i-1]*0.75
        for (slotId,minBid,maxBid) in slots:
            utilities.append(clicks[slotId]*(self.value - minBid))

        return utilities
    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]
    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - p_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - p_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)
        hisSpend = history.agents_spent
        self.spending = hisSpend[self.id]
        # TODO: Fill this in.
        bid = 0  # change this
        clicks = prev_round.clicks

        def calculateClicks(t, history):
            topslotClicks = round(30*math.cos(math.pi*t/24) + 50)
            numSlots = max(1, history.n_agents-1) 
            return [round(topslotClicks * pow(.75, i)) for i in range(numSlots)]
        newClicks = calculateClicks(t, history)
        if len(prev_round.slot_payments) <= 2:
        	return reserve + 1
        if min_bid >= self.value:
            bid = self.value
        else:
            if slot > 0:
                bid = self.value - (newClicks[slot] * (self.value - min_bid) / newClicks[slot - 1])
            else:
                bid = self.value

        moneyLeft = self.budget - self.spending
        moneySpend = bid * clicks[0]
        if (moneySpend + self.spending) > self.budget or ((48-t)*reserve * clicks[0]) > moneyLeft:
            return reserve + 1
    	return bid
    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


