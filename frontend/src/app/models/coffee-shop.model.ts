export interface CoffeeShop {
    name: string;
    coordinates: [number, number];
    website: {
        url: string | null;
        accessible: boolean | null;
    };
    menu: {
        menu_url: string | null;
    };
    menuItems: MenuItem[];
}

export interface MenuItem {
    name: string;
    price: number;
}