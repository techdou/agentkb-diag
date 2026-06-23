import React, { createContext, useContext, useReducer, Dispatch } from 'react';
import type { RoundName, SidebarView } from '../types';

export type AppState = {
  datasetId: string;
  selectedRound: RoundName;
  selectedPageId?: string;
  selectedClaimId?: string;
  selectedQueryId?: string;
  selectedIssueType?: string;
  sidebarView: SidebarView;
};

type Action =
  | { type: 'SET_DATASET'; payload: string }
  | { type: 'SET_SELECTED_ROUND'; payload: RoundName }
  | { type: 'SET_SELECTED_PAGE_ID'; payload: string | undefined }
  | { type: 'SET_SELECTED_CLAIM_ID'; payload: string | undefined }
  | { type: 'SET_SELECTED_QUERY_ID'; payload: string | undefined }
  | { type: 'SET_SELECTED_ISSUE_TYPE'; payload: string | undefined }
  | { type: 'SET_SIDEBAR_VIEW'; payload: SidebarView };

const initialState: AppState = {
  datasetId: 'demo',
  selectedRound: 'round_1',
  selectedPageId: undefined,
  selectedClaimId: undefined,
  selectedQueryId: undefined,
  selectedIssueType: undefined,
  sidebarView: 'overview',
};

function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_DATASET':
      return { ...state, datasetId: action.payload };
    case 'SET_SELECTED_ROUND':
      return { ...state, selectedRound: action.payload };
    case 'SET_SELECTED_PAGE_ID':
      return { ...state, selectedPageId: action.payload };
    case 'SET_SELECTED_CLAIM_ID':
      return { ...state, selectedClaimId: action.payload };
    case 'SET_SELECTED_QUERY_ID':
      return { ...state, selectedQueryId: action.payload };
    case 'SET_SELECTED_ISSUE_TYPE':
      return { ...state, selectedIssueType: action.payload };
    case 'SET_SIDEBAR_VIEW':
      return { ...state, sidebarView: action.payload };
    default:
      return state;
  }
}

const AppStateContext = createContext<AppState>(initialState);
const AppDispatchContext = createContext<Dispatch<Action>>(() => {});

export function AppStateProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);
  return (
    <AppStateContext.Provider value={state}>
      <AppDispatchContext.Provider value={dispatch}>
        {children}
      </AppDispatchContext.Provider>
    </AppStateContext.Provider>
  );
}

export function useAppState() {
  return useContext(AppStateContext);
}

export function useAppDispatch() {
  return useContext(AppDispatchContext);
}
