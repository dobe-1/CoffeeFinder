export interface CoffeeShop {
    name: string;
    coordinates: [number, number];
    website: {
        url: string | null;
        accessible: boolean | null;
    };
    menuItems: MenuItem[];
}

export interface MenuItem {
    name: string;
    price: number;
}